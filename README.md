# Erlastic #

## Usage ##

Erlastic allows you to serialize/deserialize python objects into 
[erlang binary term](http://erlang.org/doc/apps/erts/erl_ext_dist.html).

Basic usage is :
    
    import erlastic
    py_struct = erlastic.decode(binary_term)
    binary = erlastic.encode(py_struct)

## Erlang Port communication usage

The library contains also a function to use python with erlastic in an erlang
port to communicate erlang binary term : `port_communication()` which return
`(mailbox,port)`. They are both python coroutines (executed generator) so you
can communicate with erlang coroutine using python abstractions :

- `mailbox` waits for port message in stdin, iterating over messages decoded
   from binary erlang term format.
- `port` waits for `send(python_struct)` (http://docs.python.org/3.3/reference/expressions.html#generator.send)
  then encode `python_struct` into binary term format and send it to the erlang port via stdout.

So for instance, if you want to create a Python server which
receives the tuple {A,B} and return {ok,A/B} of {error,divisionbyzero} 
you can use at the python side :

    from erlastic import port_connection,Atom as A
    mailbox,port = port_connection()
    
    for (a,b) in mailbox:
      port.send((A("ok"),a/b) if b!=0 else (A("error"),A("divisionbyzero")))

and at the erlang side, use `-u` python parameter to prevent python output
buffering, use 4 bytes packet length because it is the configuration used by
the python generators.

    Port = open_port({spawn,"python3 -u add_server.py"},[binary,{packet,4}]),
    Div = fun(A,B)->
      Port ! {self(),{command,term_to_binary({A,B})}},
      receive {Port,{data,Bin}}->binary_to_term(Bin) after 1000->{error,timeout} end
    end,
    io:format("send {A,B}=~p, python result : ~p~n",[{32,10},Div(32,10)]),
    io:format("send {A,B}=~p, python result : ~p~n",[{2,0},Div(2,0)]),
    io:format("send {A,B}=~p, python result : ~p~n",[{1,1},Div(1,1)])

or in elixir :

    port = Port.open({:spawn,'python3 -u add_server.py'},[:binary|[packet: 4]])
    div = fn(a,b)->
      port <- {self,{:command,term_to_binary({a,b})}}
      receive do {_,{:data,b}} -> binary_to_term(b) after 100->{:error,:timeout} end
    end
    IO.puts "send {a,b}={32,10}, python result : #{inspect div.(32,10)}"
    IO.puts "send {a,b}={2,0}, python result : #{inspect div.(2,0)}"
    IO.puts "send {a,b}={1,1}, python result : #{inspect div.(1,1)}"
