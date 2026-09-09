use inodefs::{Error, InodeFs, ROOT_INODE};
use std::io::{self, Write};
use std::path::PathBuf;

fn main() {
    println!("=== InodeFS CLI ===");
    println!("支援指令：format, mount, ls, mkdir, touch, cat, write, rm, rmdir, stat, chmod, cd, pwd, sync, quit");
    println!();

    let mut fs: Option<InodeFs> = None;
    let mut cwd: u32 = ROOT_INODE;

    loop {
        let prompt = if fs.is_some() {
            format!("inodefs:{}> ", cwd)
        } else {
            "inodefs> ".to_string()
        };

        print!("{}", prompt);
        io::stdout().flush().unwrap();

        let mut input = String::new();
        if io::stdin().read_line(&mut input).unwrap() == 0 {
            break;
        }

        let input = input.trim();
        if input.is_empty() {
            continue;
        }

        let parts: Vec<&str> = input.splitn(2, ' ').collect();
        let cmd = parts[0].to_lowercase();

        match cmd.as_str() {
            "format" => {
                if parts.len() < 2 {
                    println!("用法：format <路徑>");
                    continue;
                }
                let path = PathBuf::from(parts[1]);
                match InodeFs::format(&path) {
                    Ok(new_fs) => {
                        fs = Some(new_fs);
                        cwd = ROOT_INODE;
                        println!("已格式化並掛載：{}", parts[1]);
                    }
                    Err(e) => println!("錯誤：{}", e),
                }
            }

            "mount" => {
                if parts.len() < 2 {
                    println!("用法：mount <路徑>");
                    continue;
                }
                let path = PathBuf::from(parts[1]);
                match InodeFs::mount(&path) {
                    Ok(new_fs) => {
                        fs = Some(new_fs);
                        cwd = ROOT_INODE;
                        println!("已掛載：{}", parts[1]);
                    }
                    Err(e) => println!("錯誤：{}", e),
                }
            }

            "ls" => {
                let fs = match fs.as_mut() {
                    Some(f) => f,
                    None => {
                        println!("請先 format 或 mount 一個磁碟");
                        continue;
                    }
                };

                let target_ino = if parts.len() > 1 && !parts[1].is_empty() {
                    match resolve_path(fs, cwd, parts[1]) {
                        Ok(ino) => ino,
                        Err(e) => {
                            println!("錯誤：{}", e);
                            continue;
                        }
                    }
                } else {
                    cwd
                };

                match list_directory(fs, target_ino) {
                    Ok(entries) => {
                        if entries.is_empty() {
                            println!("(空目錄)");
                        } else {
                            for (name, ino, ft) in entries {
                                println!("{:6} {:4} {}", ft, ino, name);
                            }
                        }
                    }
                    Err(e) => println!("錯誤：{}", e),
                }
            }

            "mkdir" => {
                let fs = match fs.as_mut() {
                    Some(f) => f,
                    None => {
                        println!("請先 format 或 mount 一個磁碟");
                        continue;
                    }
                };

                if parts.len() < 2 {
                    println!("用法：mkdir <名稱>");
                    continue;
                }
                match fs.mkdir(cwd, parts[1], 0o755) {
                    Ok(ino) => println!("已建立目錄，inode: {}", ino),
                    Err(e) => println!("錯誤：{}", e),
                }
            }

            "touch" => {
                let fs = match fs.as_mut() {
                    Some(f) => f,
                    None => {
                        println!("請先 format 或 mount 一個磁碟");
                        continue;
                    }
                };

                if parts.len() < 2 {
                    println!("用法：touch <檔案名>");
                    continue;
                }
                match fs.create(cwd, parts[1], 0o644, 0, 0) {
                    Ok(ino) => println!("已建立檔案，inode: {}", ino),
                    Err(e) => println!("錯誤：{}", e),
                }
            }

            "cat" => {
                let fs = match fs.as_mut() {
                    Some(f) => f,
                    None => {
                        println!("請先 format 或 mount 一個磁碟");
                        continue;
                    }
                };

                if parts.len() < 2 {
                    println!("用法：cat <檔案名>");
                    continue;
                }
                match read_file(fs, cwd, parts[1]) {
                    Ok(content) => {
                        println!("{}", String::from_utf8_lossy(&content));
                    }
                    Err(e) => println!("錯誤：{}", e),
                }
            }

            "write" => {
                let fs = match fs.as_mut() {
                    Some(f) => f,
                    None => {
                        println!("請先 format 或 mount 一個磁碟");
                        continue;
                    }
                };

                let args: Vec<&str> = input.splitn(3, ' ').collect();
                if args.len() < 3 {
                    println!("用法：write <檔案名> <內容>");
                    continue;
                }
                let content = args[2];
                match write_file(fs, cwd, args[1], content.as_bytes()) {
                    Ok(_) => println!("已寫入"),
                    Err(e) => println!("錯誤：{}", e),
                }
            }

            "rm" => {
                let fs = match fs.as_mut() {
                    Some(f) => f,
                    None => {
                        println!("請先 format 或 mount 一個磁碟");
                        continue;
                    }
                };

                if parts.len() < 2 {
                    println!("用法：rm <檔案名>");
                    continue;
                }
                match fs.unlink(cwd, parts[1]) {
                    Ok(_) => println!("已刪除"),
                    Err(e) => println!("錯誤：{}", e),
                }
            }

            "rmdir" => {
                let fs = match fs.as_mut() {
                    Some(f) => f,
                    None => {
                        println!("請先 format 或 mount 一個磁碟");
                        continue;
                    }
                };

                if parts.len() < 2 {
                    println!("用法：rmdir <目錄名>");
                    continue;
                }
                match fs.rmdir(cwd, parts[1]) {
                    Ok(_) => println!("已刪除目錄"),
                    Err(e) => println!("錯誤：{}", e),
                }
            }

            "stat" => {
                let fs = match fs.as_mut() {
                    Some(f) => f,
                    None => {
                        println!("請先 format 或 mount 一個磁碟");
                        continue;
                    }
                };

                if parts.len() < 2 {
                    println!("用法：stat <名稱>");
                    continue;
                }
                match stat(fs, cwd, parts[1]) {
                    Ok(info) => println!("{}", info),
                    Err(e) => println!("錯誤：{}", e),
                }
            }

            "chmod" => {
                let fs = match fs.as_mut() {
                    Some(f) => f,
                    None => {
                        println!("請先 format 或 mount 一個磁碟");
                        continue;
                    }
                };

                let args: Vec<&str> = input.splitn(3, ' ').collect();
                if args.len() < 3 {
                    println!("用法：chmod <名稱> <octal權限>");
                    continue;
                }
                let mode = match u16::from_str_radix(args[2], 8) {
                    Ok(m) => m,
                    Err(_) => {
                        println!("無效的權限：{}", args[2]);
                        continue;
                    }
                };
                match chmod(fs, cwd, args[1], mode) {
                    Ok(_) => println!("已修改權限"),
                    Err(e) => println!("錯誤：{}", e),
                }
            }

            "cd" => {
                let fs = match fs.as_mut() {
                    Some(f) => f,
                    None => {
                        println!("請先 format 或 mount 一個磁碟");
                        continue;
                    }
                };

                let target = if parts.len() > 1 && !parts[1].is_empty() {
                    parts[1]
                } else {
                    ""
                };

                match change_dir(fs, &mut cwd, target) {
                    Ok(_) => {}
                    Err(e) => println!("錯誤：{}", e),
                }
            }

            "pwd" => {
                let fs = match fs.as_mut() {
                    Some(f) => f,
                    None => {
                        println!("請先 format 或 mount 一個磁碟");
                        continue;
                    }
                };

                print_path(fs, cwd);
                println!();
            }

            "sync" => {
                let fs = match fs.as_mut() {
                    Some(f) => f,
                    None => {
                        println!("請先 format 或 mount 一個磁碟");
                        continue;
                    }
                };

                match fs.sync() {
                    Ok(_) => println!("已同步"),
                    Err(e) => println!("錯誤：{}", e),
                }
            }

            "quit" | "exit" => {
                if let Some(ref mut fs) = fs {
                    let _ = fs.sync();
                }
                println!("再見！");
                break;
            }

            "help" => {
                println!("支援指令：");
                println!("  format <路徑>         - 格式化新磁碟");
                println!("  mount <路徑>          - 掛載現有磁碟");
                println!("  ls [目錄]            - 列出目錄內容");
                println!("  mkdir <名稱>          - 建立目錄");
                println!("  touch <檔案名>        - 建立空檔案");
                println!("  cat <檔案名>          - 顯示檔案內容");
                println!("  write <檔案名> <內容> - 寫入檔案");
                println!("  rm <檔案名>           - 刪除檔案");
                println!("  rmdir <目錄名>        - 刪除目錄");
                println!("  cd [目錄]             - 切換目錄");
                println!("  pwd                  - 顯示目前路徑");
                println!("  stat <名稱>           - 顯示檔案狀態");
                println!("  chmod <名稱> <octal>  - 改變權限");
                println!("  sync                  - 同步到磁碟");
                println!("  quit                  - 離開");
            }

            _ => {
                println!("未知指令：{}，輸入 help 查看說明", cmd);
            }
        }
    }
}

fn resolve_path(fs: &mut InodeFs, cwd: u32, path: &str) -> Result<u32, Error> {
    if path.is_empty() {
        return Ok(cwd);
    }

    let mut current = cwd;
    for component in path.split('/').filter(|s| !s.is_empty()) {
        match component {
            "." => continue,
            ".." => {
                if current != ROOT_INODE {
                    current = get_parent(fs, current)?;
                }
            }
            _ => {
                let ino = fs.lookup_inode(current, component)?;
                current = ino.ok_or_else(|| Error::NotFound(component.into()))?;
            }
        }
    }
    Ok(current)
}

fn get_parent(fs: &mut InodeFs, ino: u32) -> Result<u32, Error> {
    let dir = fs.read_directory(ino)?;
    for entry in dir.entries() {
        if entry.name == ".." {
            return Ok(entry.inode);
        }
    }
    Ok(ROOT_INODE)
}

fn list_directory(fs: &mut InodeFs, ino: u32) -> Result<Vec<(String, u32, String)>, Error> {
    let dir = fs.read_directory(ino)?;
    let mut results = Vec::new();

    for entry in dir.entries() {
        if entry.name == "." || entry.name == ".." {
            continue;
        }
        let stat = fs.stat(entry.inode)?;
        let ft = file_type_str(stat.mode);
        results.push((entry.name.clone(), entry.inode, ft.to_string()));
    }

    Ok(results)
}

fn file_type_str(mode: u16) -> &'static str {
    match (mode >> 12) & 0xF {
        0x1 => "FIFO",
        0x2 => "CHR",
        0x4 => "DIR",
        0x6 => "BLK",
        0x8 => "REG",
        0xA => "LNK",
        0xC => "SOCK",
        _ => "UNKNOWN",
    }
}

fn read_file(fs: &mut InodeFs, cwd: u32, name: &str) -> Result<Vec<u8>, Error> {
    let ino = fs.lookup_inode(cwd, name)?.ok_or_else(|| Error::NotFound(name.into()))?;

    let stat = fs.stat(ino)?;
    if (stat.mode >> 12) & 0xF == 0x4 {
        return Err(Error::IsDirectory(name.into()));
    }

    let mut buf = vec![0u8; stat.size as usize];
    fs.read(ino, 0, &mut buf)?;
    Ok(buf)
}

fn write_file(fs: &mut InodeFs, cwd: u32, name: &str, data: &[u8]) -> Result<(), Error> {
    let ino = fs.lookup_inode(cwd, name)?.ok_or_else(|| Error::NotFound(name.into()))?;
    fs.write(ino, 0, data)?;
    fs.sync()?;
    Ok(())
}

fn stat(fs: &mut InodeFs, cwd: u32, name: &str) -> Result<String, Error> {
    let ino = fs.lookup_inode(cwd, name)?.ok_or_else(|| Error::NotFound(name.into()))?;
    let s = fs.stat(ino)?;
    let ft = file_type_str(s.mode);

    Ok(format!(
        "inode: {}
類型: {}
權限: {:o}
大小: {} bytes
連結數: {}
blocks: {}",
        s.ino, ft, s.mode & 0x1FF, s.size, s.links, s.blocks
    ))
}

fn chmod(fs: &mut InodeFs, cwd: u32, name: &str, mode: u16) -> Result<(), Error> {
    let ino = fs.lookup_inode(cwd, name)?.ok_or_else(|| Error::NotFound(name.into()))?;
    fs.chmod(ino, mode)?;
    fs.sync()?;
    Ok(())
}

fn change_dir(fs: &mut InodeFs, cwd: &mut u32, name: &str) -> Result<(), Error> {
    let target = if name.is_empty() || name == "/" {
        ROOT_INODE
    } else {
        resolve_path(fs, *cwd, name)?
    };

    let stat = fs.stat(target)?;
    if (stat.mode >> 12) & 0xF != 0x4 {
        return Err(Error::NotDirectory(name.into()));
    }
    *cwd = target;
    Ok(())
}

fn print_path(fs: &mut InodeFs, ino: u32) {
    let mut components = Vec::new();
    let mut current = ino;

    if current == ROOT_INODE {
        print!("/");
        return;
    }

    while current != ROOT_INODE {
        let dir = fs.read_directory(current).ok();
        let parent = dir
            .as_ref()
            .and_then(|d| d.find_inode(".."))
            .unwrap_or(ROOT_INODE);

        let name = fs.read_directory(parent).ok()
            .and_then(|d| {
                d.entries()
                    .iter()
                    .find(|e| e.inode == current && e.name != ".")
                    .map(|e| e.name.clone())
            })
            .unwrap_or_else(|| "?".to_string());

        components.push(name);
        current = parent;
    }

    if components.is_empty() {
        print!("/");
    } else {
        for component in components.iter().rev() {
            print!("/{}", component);
        }
    }
}