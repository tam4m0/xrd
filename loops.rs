#[path="./messages.rs"]
pub mod messages;
#[path="./structs.rs"]
pub mod structs;
use std::net::TcpStream;
use crate::structs::*;

pub fn event(socket: TcpStream, handler: u32, cnfroot: Config) {
	loop {
		let message = messages::listen(socket.try_clone().unwrap()).unwrap_or_else(|_str| "".to_string());
		if message == "" || message.contains("methodResponse") {
			continue;
		} else { 
			let (meth_name, meth_argv) = messages::reverse_xmlrpc(message);
			if meth_name.starts_with("TrackMania.PlayerChat") {
				if meth_argv[2].starts_with(&format!("{}{}",&cnfroot.main.prefix,String::from("echo"))[..]) {
					let user = &meth_argv[1];
					let (mut stream, mut handler2) = messages::send_message(messages::transform_xmlrpc(format!("mc
mn ChatSendToLogin
pa
paa va str {}
paa va str {}","cirno",user)),socket.try_clone().unwrap(),handler).unwrap();
				}
			}
		}
	}
}
