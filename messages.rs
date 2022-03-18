extern crate quick_xml;
use serde::*;
use byteorder::{ByteOrder,LittleEndian};
use std::str;
use std::net::TcpStream;
use std::io::prelude::*;
use quick_xml::Writer;
use quick_xml::se::Serializer;
use aho_corasick::AhoCorasick;
#[path="./structs.rs"]
pub mod structs;

pub fn transform_xmlrpc(lang: String) -> String {
	let mut langlist = lang.split("\n").collect::<Vec<&str>>();
	let ac = AhoCorasick::new_auto_configured(&["str","bool","i4"]);
	let mut langstr = String::new();
	if langlist[0] == "mc" {
		langstr.push_str("<methodCall>");
		let mut methodName = langlist[1].split(" ").collect::<Vec<&str>>()[1];
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
							langstr.push_str(&format!("<string>{}</string>",x[3])[..]);
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


pub fn send_message(str: String, mut stream: TcpStream, handler: &mut u32) -> Result<(TcpStream,u32),()> {
        let mut handler_bytes = [0;4];
        let mut len_bytes = [0;4];
        if *handler + 1 == 0xFFFFFFFF { *handler = 0x80000000; } else { *handler += 1; }
        LittleEndian::write_u32(&mut handler_bytes, *handler);
        LittleEndian::write_u32(&mut len_bytes, *&str.as_bytes().len() as u32);
        let a = stream.write(&len_bytes);
        let b = stream.write(&handler_bytes);
        let c = stream.write(&str.as_bytes());
        for x in [a,b,c].iter() {
                if !x.is_ok() {
                        return Err(());
                }
        }
        Ok((stream,*handler))
}

pub fn listen(socket: &mut TcpStream) -> Result<String,()> {
	loop {
		let mut buf = [0;1024];
		let mut res = socket.read(&mut buf);
		if !res.is_ok() { return Err(()); }
		if buf.is_empty() { continue; }

		buf = [0;1024];
		res = socket.read(&mut buf);
		if !res.is_ok() { return Err(()); }
		if buf.is_empty() { continue; }

		let str = str::from_utf8(&buf).unwrap().trim_matches(char::from(0)).to_string();
		return Ok(str);
	}
}
