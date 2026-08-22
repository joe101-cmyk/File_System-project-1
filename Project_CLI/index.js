import fs from "fs/promises";
import path from "path"
import { close_readline, get_path} from "./Get_path.js";


async function read_File(){
try {
    let count_Fille = 0 , count_Folder = 0;
    const path_now = await get_path();
    // console.log("path_now : ",path_now);
    
    const filles = await fs.readdir(path_now,{
        withFileTypes:true
    })
    // console.log("Filles : ",filles);

        for(const file of filles ){
        if(file.isFile()){
            console.log(file.name,"Filles");
            count_Fille++;
        }
        if(file.isDirectory()){
            console.log(file.name,"Folder");
            count_Folder++;
        }
            
    }
        console.log("Folder : ",path.basename(path_now));
        
    console.log(`count Fille = ${count_Fille}`);
    console.log(`Count Folder = ${count_Folder}`);
    

    
}
catch (err) {
    console.error(`error: could not read folder: ${path_now}`);
    process.exitCode = 1;
}

close_readline()
}


read_File()
