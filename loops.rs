#[path="./messages.rs"]
pub mod messages;
#[path="./structs.rs"]
pub mod structs;
use std::str;
use std::net::TcpStream;
use std::sync::{Arc,Mutex};
use rand::thread_rng;
use rand::seq::SliceRandom;
use aho_corasick::AhoCorasick;
use walkdir::WalkDir;
use crate::structs::*;

fn skipToChallenge(socket: Arc<Mutex<TcpStream>>, mut handler: Arc<Mutex<u32>>, argstr: String) -> Arc<Mutex<u32>> {
	handler = messages::send_message(messages::transform_xmlrpc(format!("mc
mn InsertChallenge
pa
paa va str {}",argstr)),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1;
	handler = messages::send_message(messages::transform_xmlrpc("mc
mn NextChallenge
pa".to_string()),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1;
	handler
}

fn ban(socket: Arc<Mutex<TcpStream>>, mut handler: Arc<Mutex<u32>>, server: &Server, user: String) -> Arc<Mutex<u32>> {
	if server.gametype == "forever" {
		handler = messages::send_message(messages::transform_xmlrpc(format!("mc
mn BanAndBlackList
pa
paa va str {}
paa va str The ban hammer has spoken!
paa va bool true",user)),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1;
	} else {
		handler = messages::send_message(messages::transform_xmlrpc(format!("mc
mn Ban
pa
paa va str {}",user)),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1;
	}
	handler
}

fn kick(socket: Arc<Mutex<TcpStream>>, mut handler: Arc<Mutex<u32>>, server: &Server, user: String) -> Arc<Mutex<u32>> {
	if server.gametype == "forever" {
		handler = messages::send_message(messages::transform_xmlrpc(format!("mc
mn Kick
pa
paa va str {}
paa va str Get outta here!",user)),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1;
	} else {
		handler = messages::send_message(messages::transform_xmlrpc(format!("mc
mn Kick
pa
paa va str {}",user)),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1;
	}
	handler
}

fn user_list(socket: Arc<Mutex<TcpStream>>, mut handler: Arc<Mutex<u32>>, server: &Server, user: String) -> Arc<Mutex<u32>> {
	if server.gametype == "forever" {
		handler = messages::send_message(messages::transform_xmlrpc("mc
mn GetPlayerList
pa
paa va i4 9999
paa va i4 0
paa va i4 0".to_string()),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1;
		let message = messages::listen(Arc::clone(&socket));
		let (meth_name, meth_argv) = messages::reverse_xmlrpc(&message);
		if meth_name.is_empty() {
			for x in meth_argv.iter().filter(|x| x.parse::<u32>().is_err()).collect::<Vec<&String>>() {
				handler = messages::send_message(messages::transform_xmlrpc(format!("mc
mn ChatSendToLogin
pa
paa va str {}
paa va str {}",if x == "-1" { continue; } else { &x },user)),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1;
			}
		}
	} else {
		handler = messages::send_message(messages::transform_xmlrpc("mc
mn GetPlayerList
pa
paa va i4 9999
paa va i4 0".to_string()),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1;
		let message = messages::listen(Arc::clone(&socket));
		let (meth_name, meth_argv) = messages::reverse_xmlrpc(&message);
		if meth_name.is_empty() {
			for x in meth_argv.iter().filter(|x| x.parse::<u32>().is_err()).collect::<Vec<&String>>() {
				handler = messages::send_message(messages::transform_xmlrpc(format!("mc
mn ChatSendToLogin
pa
paa va str {}
paa va str {}",if x == "-1" { continue; } else { &x },user)),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1;
			}
		}
	}
	handler
}

fn chall_list(socket: Arc<Mutex<TcpStream>>, mut handler: Arc<Mutex<u32>>, user: String, config: &Server) -> Arc<Mutex<u32>> {
	for e in WalkDir::new(&config.trackspath).follow_links(false).into_iter().filter_map(|x| x.ok()) {
		handler = messages::send_message(messages::transform_xmlrpc(format!("mc
mn ChatSendToLogin
pa
paa va str {}
paa va str {}",&format!("{:?}",e).as_str()[format!("{:?}",e).rfind('/').unwrap()+1..format!("{:?}",e).rfind("\")").unwrap()].to_string(),user)),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1
	}
	handler
}

pub fn event((socket,mut handler): (Arc<Mutex<TcpStream>>,Arc<Mutex<u32>>), (main,server): (&Main,&Server)) {
	let mut rng = thread_rng();
	let admins = server.admins.split("**").collect::<Vec<&str>>();
	let ac_useractions = AhoCorasick::new_auto_configured(&["kick", "ban", "list"]);
	let ac_challactions = AhoCorasick::new_auto_configured(&["skip","remove","insert","list"]);
	loop {
		let message = messages::listen(Arc::clone(&socket));
		let (meth_name, meth_argv) = messages::reverse_xmlrpc(&message);
		if meth_name.starts_with("TrackMania.StatusChanged") {
			if meth_argv[1].starts_with("Running - Finish") && server.gametype == "forever" {
				let mut choice: String = WalkDir::new(&server.songspath).follow_links(false).into_iter().filter_map(|x| x.ok()).map(|x| format!("{:?}",x)).collect::<Vec<String>>().choose(&mut rng).unwrap().to_string();
				choice = choice[..][choice.find("(\"").unwrap()+2..choice.find("\")").unwrap()].to_string();
				handler = messages::send_message(messages::transform_xmlrpc(format!("mc
mn SetForcedMusic
pa
paa va bool true
paa va str {}",choice)),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1;
			}
		}
		if meth_name.starts_with("TrackMania.PlayerChat") {
			if meth_argv[2].starts_with(&format!("{}{}",main.prefix,String::from("help"))[..]) {
				let user = &meth_argv[1];
				let helpstrs = vec![String::from("/help: The command you're viewing right now."),String::from("/echo: Echoes whatever you put into it, but only to you."),String::from("/hacktheplanet: Free Kevin!"),String::from("/user list: Lists all users."),String::from("/user kick: Kicks a user."),String::from("/user ban: Bans a user."),String::from("/chall skip: Skips to a challenge."),String::from("/chall remove: Removes a challenge."),String::from("/chall insert: Inserts a challenge."),String::from("/chall list: Lists all challenges.")];
				for helpstr in helpstrs {
					handler = messages::send_message(messages::transform_xmlrpc(format!("mc
mn ChatSendToLogin
pa
paa va str {}
paa va str {}",helpstr,user)),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1;
				}
			}else if meth_argv[2].starts_with(&format!("{}{}",main.prefix,String::from("echo"))[..]) {
				let user = &meth_argv[1];
				handler = messages::send_message(messages::transform_xmlrpc(format!("mc
mn ChatSendToLogin
pa
paa va str {}
paa va str {}",meth_argv[2].split(' ').collect::<Vec<&str>>()[1..].join(" "),user)),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1;
			}else if meth_argv[2].starts_with(&format!("{}{}",main.prefix,String::from("hacktheplanet"))[..]) {
				if server.gametype == "forever" {
					let user = &meth_argv[1];
					handler = messages::send_message(messages::transform_xmlrpc(format!("mc
mn Kick
pa
paa va str {}
paa va str The CIA has arrested you for hacking, GG.",user)),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1;
				} else {
					let user = &meth_argv[1];
					handler = messages::send_message(messages::transform_xmlrpc(format!("mc
mn ChatSendToLogin
pa
paa va str The CIA has arrested you for hacking, GG.
paa va str {}",user)),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1;
					handler = messages::send_message(messages::transform_xmlrpc(format!("mc
mn Kick
pa
paa va str {}",user)),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1;
				}
			}else if meth_argv[2].starts_with(&format!("{}{}",main.prefix,String::from("user"))[..]) {
				let user = &meth_argv[1];
				let argstr = &meth_argv[2].split(' ').collect::<Vec<&str>>()[1..];
				if !argstr.is_empty() && admins.contains(&user.as_str()) && ac_useractions.is_match(argstr[0]) {
					let mat = ac_useractions.find(argstr[0]).unwrap();
					match mat {
						_ if mat.pattern() == 0 => handler = kick(Arc::clone(&socket),Arc::clone(&handler),&server,argstr[1].to_string()),
						_ if mat.pattern() == 1 => handler = ban(Arc::clone(&socket),Arc::clone(&handler),&server,argstr[1].to_string()),
						_ if mat.pattern() == 2 => handler = user_list(Arc::clone(&socket),Arc::clone(&handler),&server,user.to_string()),
						_ => nop(),
					};
				}
			}else if meth_argv[2].starts_with(&format!("{}{}",main.prefix,String::from("chall"))[..]) {
				let user = &meth_argv[1];
				let argstr = &meth_argv[2].split(' ').collect::<Vec<&str>>()[1..];
				if !argstr.is_empty() && admins.contains(&user.as_str()) && ac_challactions.is_match(argstr[0]) {
					let mat = ac_challactions.find(argstr[0]).unwrap();
					match mat {
						_ if mat.pattern() == 0 => handler = skipToChallenge(Arc::clone(&socket),Arc::clone(&handler),format!("{}/{}",&server.trackspath,argstr[1..].join(" "))),
						_ if mat.pattern() == 1 => handler = messages::send_message(messages::transform_xmlrpc(format!("mc
mn RemoveChallenge
paa va str {}",format!("{}/{}",&server.trackspath,argstr[1..].join(" ")))),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1,
						_ if mat.pattern() == 2 => handler = messages::send_message(messages::transform_xmlrpc(format!("mc
mn InsertChallenge
paa va str {}",format!("{}/{}",&server.trackspath,argstr[1..].join(" ")))),Arc::clone(&socket),Arc::clone(&handler)).unwrap().1,
						_ if mat.pattern() == 3 => handler = chall_list(Arc::clone(&socket),Arc::clone(&handler),user.to_string(),&server),
						_ => nop(),
					}
				}
			}
		}
	}
}
