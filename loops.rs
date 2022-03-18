#[path="./messages.rs"]
pub mod messages;
#[path="./structs.rs"]
pub mod structs;
use std::net::TcpStream;
use std::sync::{Arc,Mutex};
use aho_corasick::AhoCorasick;
use crate::structs::*;

fn splitArgs(argv: &String, cmd: String) -> Vec<String> {
	argv.split(&cmd).into_iter().filter(|x| x != &"/").map(|x| String::from(x.trim())).collect::<Vec<String>>()
}

pub fn event(socket: Arc<Mutex<TcpStream>>, handler: u32, cnfroot: Config) {
	let ac_admins = AhoCorasick::new_auto_configured(&(&cnfroot.server.admins).split(":").collect::<Vec<&str>>()[..]);
	loop {
		let message = messages::listen(Arc::clone(&socket));
		if message.contains("methodResponse") {
			continue;
		} else { 
			let (meth_name, meth_argv) = messages::reverse_xmlrpc(message);
			if meth_name.starts_with("TrackMania.PlayerChat") {
				if meth_argv[2].starts_with(&format!("{}{}",&cnfroot.main.prefix,String::from("echo"))) {
					let cmd = &format!("{}{}",&cnfroot.main.prefix,String::from("echo"));
					let user = &meth_argv[1];
					let mut argstr = splitArgs(&meth_argv[2],String::from("echo"));
					messages::send_message(messages::transform_xmlrpc(format!("mc
mn ChatSendToLogin
pa
paa va str {}
paa va str {}",argstr.join(" "),user)),Arc::clone(&socket),handler).unwrap();
				}if meth_argv[2].starts_with(&format!("{}{}",&cnfroot.main.prefix,String::from("hacktheplanet"))) {
					let user = &meth_argv[1];
					messages::send_message(messages::transform_xmlrpc(format!("mc
mn Kick
pa
paa va str {}
paa va str The CIA has arrested you for hacking, GG.",user)),Arc::clone(&socket),handler).unwrap();
				}if meth_argv[2].starts_with(&format!("{}{}",&cnfroot.main.prefix,String::from("ban"))) {
					let user = &meth_argv[1];
					if ac_admins.is_match(user) {
						let cmd = &format!("{}{}",&cnfroot.main.prefix,String::from("ban"));
						let mut argstr = splitArgs(&meth_argv[2],String::from("ban"));
						messages::send_message(messages::transform_xmlrpc(format!("mc
mn BanAndBlackList
pa
paa va str {}
paa va str The ban hammer has spoken!
paa va bool true",argstr[0])),Arc::clone(&socket),handler).unwrap();
					}
				}
			}
		}
	}
}
