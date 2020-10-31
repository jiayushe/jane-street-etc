open Core.Std
open Async.Std

(* HOW TO RUN
   1) Configure things in CONFIGURATION section
   2) Compile: corebuild -pkg async bot.native
   3) Run in loop: while true; do ./bot.native; sleep 1; done
*)

(* CONFIGURATION *)

(* replace REPLACEME with your team name! *)
let team_name="REPLACEME"

(* This variable dictates whether or not the bot is connecting to the prod
   or test exchange. Be careful with this switch! *)
let test_mode = true

(* This setting changes which test exchange is connected to.
   0 is prod-like
   1 is slower
   2 is empty
*)
let test_exchange_index=2

let prod_exchange_hostname="production"

let port = 20000 + if test_mode then test_exchange_index else 0

let exchange_hostname =
  if test_mode
  then "test-exch-" ^ team_name
  else prod_exchange_hostname

(* NETWORKING CODE *)

type exchange =
  { reader : Reader.t
  ; writer : Writer.t
  }

let connect exchange_hostname port ~f =
  let to_hap = Tcp.to_host_and_port exchange_hostname port in
  Tcp.with_connection to_hap (fun _socket reader writer -> f { reader; writer })

let write_to_exchange exchange msg =
  Writer.write_line exchange.writer msg

let read_from_exchange exchange =
  Reader.read_line exchange.reader

(* MAIN LOOP *)

let main () =
  connect exchange_hostname port ~f:(fun exchange ->
    write_to_exchange exchange ("HELLO " ^ String.uppercase team_name);
    (* A common mistake people make is to call write_to_exchange > 1
       time for every read_from_exchange response.
       Since many write messages generate marketdata, this will cause an
       exponential explosion in pending messages. Please, don't do that!
    *)
    match%map read_from_exchange exchange with
    | `Ok reply -> printf "The exchange replied: %s\n" reply
    | `Eof      -> eprintf "Error: Reached EOF!"
  )

let cmd =
  Command.async'
    ~summary:"my bot"
    (Command.Param.return main)

let () = Command.run cmd
