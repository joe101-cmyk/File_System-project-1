
import Readline from "readline/promises";
import { stdin, stdout } from "process";

const rl = Readline.createInterface({ input: stdin, output: stdout });

export async function get_path() {
    let entered = false;

    const question = rl.question("Enter Path: ").then((path) => {
        entered = true;
        return path;
    });

    const timeout = new Promise((resolve) => {
        setTimeout(() => {
            if (!entered) {
                rl.close();
                resolve(undefined);
            }
        }, 10000);
    });

    const File_path = await Promise.race([
        question,
        timeout
    ]);

    if (File_path !== undefined && File_path.trim() !== "") {
        return File_path;
    }

    return process.cwd();
}




export function close_readline() {
    rl.close();
}

