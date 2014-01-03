# Erlastic #

## Usage ##

Erlastic allows you to serialize/deserialize python objects into 
[erlang binary term](http://erlang.org/doc/apps/erts/erl_ext_dist.html).

Basic usage is :
    
    import erlastic
    py_struct = erlastic.decode(binary_term)
    binary = erlastic.encode(py_struct)

## Erlang Port communication usage

The library contains also two functions useful to use python with
erlastic in an erlang port to communicate erlang binary term :
`port_req` and `port_res` :

- `port_req()` is a generator waiting for port message in stdin,
  iterating over messages decoded from binary erlang term format.
- `port_res(python_response)` is a function which encode
  `python_response` and send it to the erlang port via stdout.

So for instance, if you want to create a Python server which
receives the tuple {A,B} and return {ok,A+B} you can use in the
python side :

    from erlastic import port_req,port_res,Atom
    
    for (a,b) in port_req():
      port_res((Atom("ok"),a+b))

and at the erlang side, use `-u` python parameter to prevent python output
buffering, use 4 bytes packet length because it is the configuration used by
`port_req` and `port_res`.

    Port = open_port({spawn,"python3 -u add_server.py"},[binary,{packet,4}]),
    Add = fun(A,B)->
      Port ! {self(),{command,term_to_binary({A,B})}},
      receive {Port,{data,Bin}}->binary_to_term(Bin) after 1000->{error,timeout} end
    end,
    io:format("send {A,B}=~p, python result : ~p~n",[{32,10},Add(32,10)]),
    io:format("send {A,B}=~p, python result : ~p~n",[{2,1},Add(2,1)]),
    io:format("send {A,B}=~p, python result : ~p~n",[{1,1},Add(1,1)])

or in elixir :

    port = Port.open({:spawn,'python3 -u add_server.py'},[:binary|[packet: 4]])
    add = fn(a,b)->
      port <- {self,{:command,term_to_binary({a,b})}}
      receive do {_,{:data,b}} -> binary_to_term(b) after 100->{:error,:timeout} end
    end
    IO.puts "send {a,b}={32,10}, python result : #{inspect add.(32,10)}"
    IO.puts "send {a,b}={2,1}, python result : #{inspect add.(2,1)}"
    IO.puts "send {a,b}={1,1}, python result : #{inspect add.(1,1)}"
