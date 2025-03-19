use std::fs::File;
use std::io::{self, Read, Seek};
use std::process;
use std::{env, fs};

fn get_orientation(file_path: &str) -> io::Result<String> {
    let mut file = File::open(file_path)?;
    let mut buffer = [0u8; 24];
    file.read_exact(&mut buffer)?;

    if &buffer[0..8] == b"\x89PNG\r\n\x1a\n" {
        let width = u32::from_be_bytes(buffer[16..20].try_into().unwrap());
        let height = u32::from_be_bytes(buffer[20..24].try_into().unwrap());
        //println!("Width: {}, Height: {}", width, height);
        return Ok(if height > width {
            "portrait".to_string()
        } else {
            "landscape".to_string()
        });
    }

    if buffer[6..10] == *b"JFIF" || buffer[6..10] == *b"Exif" {
        file.seek(io::SeekFrom::Start(2))?;
        let mut marker = [0u8; 2];
        loop {
            file.read_exact(&mut marker)?;
            if marker[0] != 0xFF {
                break;
            }
            if marker[1] >= 0xC0 && marker[1] <= 0xC3 {
                let mut sof = [0u8; 7];
                file.read_exact(&mut sof)?;

                let height = u16::from_be_bytes(sof[3..5].try_into().unwrap());
                let width = u16::from_be_bytes(sof[5..7].try_into().unwrap());

                //println!("Width: {}, Height: {}", width, height);
                return Ok(if height > width {
                    "portrait".to_string()
                } else {
                    "landscape".to_string()
                });
            }
            let mut length = [0u8; 2];
            file.read_exact(&mut length)?;
            let skip = u16::from_be_bytes(length) as i64 - 2;
            file.seek(io::SeekFrom::Current(skip))?;
        }
    }

    Err(io::Error::new(
        io::ErrorKind::InvalidData,
        "Unsupported file format",
    ))
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: fast_orientation <image_path>");
        process::exit(1);
    }

    let dir_path = &args[1];

    let entries = match fs::read_dir(dir_path) {
        Ok(entries) => entries,
        Err(e) => {
            eprintln!("Error reading directory {}", e);
            process::exit(1);
        }
    };

    for entry in entries {
        match entry {
            Ok(entry) => {
                let path = entry.path();
                if path.is_file() {
                    match get_orientation(path.to_str().unwrap()) {
                        Ok(orientation) => println!("{},{}", path.display(), orientation),
                        Err(e) => {
                            eprintln!("Error: {}", e);
                            process::exit(1);
                        }
                    }
                }
            }
            Err(e) => {
                eprintln!("Error reading entry {}", e)
            }
        }
    }
}
