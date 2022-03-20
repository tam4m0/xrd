use byteorder::{ByteOrder,LittleEndian};
use std::str;
use std::net::TcpStream;
use std::sync::{Arc,Mutex};
use std::io::prelude::*;
use aho_corasick::AhoCorasick;
#[path="./structs.rs"]
pub mod structs;

pub fn reverse_xmlrpc(message: &String) -> (String,Vec<String>) {
	let xmllist = message.split("\n").collect::<Vec<&str>>();
	let ac_types = AhoCorasick::new_auto_configured(&["<string>","<boolean>","<i4>","<struct>"]);
	let ac_endtypes = AhoCorasick::new_auto_configured(&["</string>","</boolean>","</i4>","</struct>"]);
	let mut methodName = String::new();
	let mut argv = Vec::new();
	if xmllist[0].starts_with("<?xml") {
		if xmllist[1].starts_with("<methodCall>") || xmllist[1].starts_with("<methodResponse>") {
			for x in &xmllist[2..] {
				if x.starts_with("<methodName>") {
					methodName.push_str(&x[x.find(">").unwrap()+1..x.rfind("<").unwrap()]);
				} if x.starts_with("<params>") { continue; }
				if x.contains("<value>") || x.starts_with("<param><value>") {
					let mat = if ac_types.find(x).is_some() { ac_types.find(x).unwrap() } else { continue; };
					let mat2 = if ac_endtypes.find(x).is_some() { ac_endtypes.find(x).unwrap() } else { continue; };
					argv.push(String::from(&x[mat.end()..mat2.start()]));
				}
			}
		} else { return (String::from("Invalid XML-RPC, check server output"),vec![String::from("Invalid XML-RPC, check server output")]); }	
	} else { return (String::from("Invalid XML-RPC, check server output"),vec![String::from("Invalid XML-RPC, check server output")]); }
	(String::from(methodName),argv)
}

pub fn transform_xmlrpc(lang: String) -> String {
	let langlist = lang.split("\n").collect::<Vec<&str>>();
	let ac = AhoCorasick::new_auto_configured(&["str","bool","i4"]);
	let mut langstr = String::new();
	if langlist[0] == "mc" {
		langstr.push_str("<methodCall>");
		let methodName = langlist[1].split(" ").collect::<Vec<&str>>()[1];
		langstr.push_str(&format!("<methodName>{}</methodName>",methodName)[..]);
		if langlist[2] == "pa" {
			langstr.push_str("<params>");
			let values = &langlist[3..];
			let mut values_vec = Vec::new();
			for x in values.iter() {
				values_vec.push(x.split(" ").collect::<Vec<&str>>());
			} for x in values_vec.iter() {
				if &x[0..2] == vec!["paa","va"] {
					langstr.push_str("<param><value>");
					if ac.is_match(x[2]) {
						if x[2] == "str" {
							langstr.push_str(&format!("<string>{}</string>",if &x[3..].len() == &usize::from(1u8) { vec![x[3]].join(" ") } else { x[3..].iter().map(|x| String::from(*x)).collect::<Vec<String>>().join(" ") })[..]);
						} else if x[2] == "bool" {
							langstr.push_str(&format!("<boolean>{}</boolean>",if x[3] == "true" { "1" } else { "0" })[..]);
						} else {
							langstr.push_str(&format!("<i4>{}</i4>",x[3])[..]);
						}
					} else { return String::from("Not valid Minified-XMLRPC."); }
					langstr.push_str("</value></param>");
				} else { return String::from("Not valid Minified-XMLRPC."); }
			} langstr.push_str("</params>");
		} else { return String::from("Not valid Minified-XMLRPC."); }
	} else { return String::from("Not valid Minified-XMLRPC."); }
	langstr.push_str("</methodCall>");
	langstr
}


pub fn send_message(str: String, stream: Arc<Mutex<TcpStream>>, handler: Arc<Mutex<u32>>) -> Result<(Arc<Mutex<TcpStream>>,Arc<Mutex<u32>>),()> {
	let cloned_stream = Arc::clone(&stream);
	let mut cloned_streamu = cloned_stream.lock().unwrap();
	let cloned_handler = Arc::clone(&handler);
	let mut cloned_handleru = cloned_handler.lock().unwrap();
        let mut handler_bytes = [0;4];
	let mut len_bytes = [0;4];
        if *cloned_handleru + 1 == 0xFFFFFFFF { *cloned_handleru = 0x80000000; } else { *cloned_handleru += 1; }
       	LittleEndian::write_u32(&mut handler_bytes, *cloned_handleru);
      	LittleEndian::write_u32(&mut len_bytes, *&str.as_bytes().len() as u32);
	let a = cloned_streamu.write(&len_bytes);
	let b = cloned_streamu.write(&handler_bytes);
	let c = cloned_streamu.write(&str.as_bytes());
	for x in [a,b,c].iter() {
	        if !x.is_ok() {
	                return Err(());
	        }
	}
	drop(cloned_streamu);
	drop(cloned_stream);
	drop(cloned_handleru);
	drop(cloned_handler);
	Ok((stream,handler))
}

pub fn listen(socket: Arc<Mutex<TcpStream>>) -> String {
	let cloned_sock = Arc::clone(&socket);
	let mut cloned_sock_unlocked = cloned_sock.lock().unwrap();
	loop {
		let mut buf = [0;1024];
		loop {
			buf = [0;1024];
			cloned_sock_unlocked.read(&mut buf).unwrap();
			if buf.is_empty() { continue; }
			if str::from_utf8(&buf).is_ok() { break; } else { continue; }
		}
		let str = &str::from_utf8(&buf).unwrap().trim_matches(char::from(0)).to_string()[..];
		let xmlstart = str.find("<?xml");
		if !xmlstart.is_some() { continue; }
		let str = str::from_utf8(&str.as_bytes()[xmlstart.unwrap() as usize..]);
		drop(cloned_sock_unlocked);
		return String::from(str.unwrap());
	}
}
