#[path="./messages.rs"]
pub mod messages;
#[path="./structs.rs"]
pub mod structs;
use std::str;
use std::usize;
use std::net::TcpStream;
use std::sync::{Arc,Mutex};
use aho_corasick::AhoCorasick;
use crate::structs::*;
use glob::glob;

fn skipToChallenge(socket: Arc<Mutex<TcpStream>>, mut handler: Arc<Mutex<u32>>, argstr: String) -> Arc<Mutex<u32>> {
	handler = messages::send_message(messages::transform_xmlrpc(format!("mc
mn InsertChallenge
pa
paa va str {}",argstr)),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1;
	handler = messages::send_message(messages::transform_xmlrpc(format!("mc
mn NextChallenge
pa")),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1;
	handler
}

fn chall_list(socket: Arc<Mutex<TcpStream>>, mut handler: Arc<Mutex<u32>>, cnfroot: &Config, user: String) -> Arc<Mutex<u32>> {
	for e in glob(format!("{}/{}",cnfroot.server.trackspath,"*").as_str()).unwrap() {
		if e.as_ref().unwrap().display().to_string().contains(".Gbx") {
			handler = messages::send_message(messages::transform_xmlrpc(format!("mc
mn ChatSendToLogin
pa
paa va str {:?}
paa va str {}",&e.as_ref().unwrap().display().to_string().as_str()[e.as_ref().unwrap().display().to_string().rfind("/").unwrap()+1..].to_string(),user)),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1
		}
	}
	handler
}

pub fn event(socket: Arc<Mutex<TcpStream>>, mut handler: Arc<Mutex<u32>>, cnfroot: &Config) {
	let ac_admins = AhoCorasick::new_auto_configured(&cnfroot.server.admins.split(":").collect::<Vec<&str>>());
	let ac_useractions = AhoCorasick::new_auto_configured(&["kick", "ban"]);
	let ac_challactions = AhoCorasick::new_auto_configured(&["skip","remove","insert","list"]);
	loop {
		let message = messages::listen(Arc::clone(&socket));
		if message.contains("methodResponse") {
			continue;
		} else {
			let (meth_name, meth_argv) = messages::reverse_xmlrpc(message);
			if meth_name.starts_with("TrackMania.PlayerChat") {
				if meth_argv[2].starts_with(&format!("{}{}",&cnfroot.main.prefix,String::from("echo"))[..]) {
					let cmd = &format!("{}{}",&cnfroot.main.prefix,String::from("echo"));
					let user = &meth_argv[1];
					handler = messages::send_message(messages::transform_xmlrpc(format!("mc
mn ChatSendToLogin
pa
paa va str {}
paa va str {}",meth_argv[2].split(" ").collect::<Vec<&str>>()[1..].join(" "),user)),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1;
				}if meth_argv[2].starts_with(&format!("{}{}",&cnfroot.main.prefix,String::from("hacktheplanet"))[..]) {
					let user = &meth_argv[1];
					handler = messages::send_message(messages::transform_xmlrpc(format!("mc
mn Kick
pa
paa va str {}
paa va str The CIA has arrested you for hacking, GG.",user)),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1;
				}if meth_argv[2].starts_with(&format!("{}{}",&cnfroot.main.prefix,String::from("user"))[..]) {
					let user = &meth_argv[1];
					let argstr = &meth_argv[2].split(" ").collect::<Vec<&str>>()[1..];
					if !argstr.is_empty() {
						if ac_admins.is_match(user) {
							if ac_useractions.is_match(argstr[0]) {
								let mat = ac_useractions.find(argstr[0]).unwrap();
								match mat {
									_ if mat.pattern() == 1 => handler = messages::send_message(messages::transform_xmlrpc(format!("mc
mn BanAndBlackList
pa
paa va str {}
paa va str The ban hammer has spoken!
paa va bool true",argstr[1])),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1,
									_ if mat.pattern() == 0 => handler = messages::send_message(messages::transform_xmlrpc(format!("mc
mn Kick
pa
paa va str {}
paa va str Get outta here!",argstr[1])),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1,
									_ => nop(),
								};
							}
						}
					}
				}if meth_argv[2].starts_with(&format!("{}{}",&cnfroot.main.prefix,String::from("chall"))[..]) {
					let user = &meth_argv[1];
					let argstr = &meth_argv[2].split(" ").collect::<Vec<&str>>()[1..];
					if !argstr.is_empty() {
						println!("{}/{}",&cnfroot.server.trackspath,argstr[1..].join(" "));
						if ac_admins.is_match(user) {
							if ac_challactions.is_match(argstr[0]) {
								let mat = ac_challactions.find(argstr[0]).unwrap();
								match mat {
									_ if mat.pattern() == 0 => handler = skipToChallenge(Arc::clone(&socket),Arc::clone(&handler),format!("{}/{}",&cnfroot.server.trackspath,argstr[1..].join(" "))),
									_ if mat.pattern() == 1 => handler = messages::send_message(messages::transform_xmlrpc(format!("mc
mn RemoveChallenge
paa va str {}",format!("{}/{}",&cnfroot.server.trackspath,argstr[1..].join(" ")))),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1,
									_ if mat.pattern() == 2 => handler = messages::send_message(messages::transform_xmlrpc(format!("mc
mn InsertChallenge
paa va str {}",format!("{}/{}",&cnfroot.server.trackspath,argstr[1..].join(" ")))),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1,
									_ if mat.pattern() == 3 => handler = chall_list(Arc::clone(&socket),Arc::clone(&handler),cnfroot,user.to_string()),
									_ => nop(),
								}
							}
						}
					}
				}
			}
		}
	}
}
