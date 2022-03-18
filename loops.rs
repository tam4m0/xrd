extern crate quick_xml;
#[path="./messages.rs"]
pub mod messages;
#[path="./structs.rs"]
pub mod structs;
use std::net::TcpStream;
use std::str;
use std::io::Cursor;
use crate::structs::*;
use quick_xml::de::*;

/*
<?xml version="1.0" encoding="UTF-8"?>
<methodCall>
<methodName>TrackMania.PlayerChat</methodName>
<params>
<param><value><i4>250</i4></value></param>
<param><value><string>irohia</string></value></param>
<param><value><string>/help</string></value></param>
<param><value><boolean>1</boolean></value></param>
</params>
</methodCall>
*/

pub fn event(ref mut socket: TcpStream, handler: u32) {
	loop {
		let mut message = messages::listen(socket).unwrap_or_else(|_str| "".to_string());
		if message == "" || message.contains("methodResponse") {
			continue;
		} else { 
			message.remove(0);
			println!("{}",message);
		}
	}
}
