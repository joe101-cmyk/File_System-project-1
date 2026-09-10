


const Tasks = []


const Add_Task = ()=>{
    let task = {
    id:Date.now(),
    description:document.getElementById("dec").value,
    completed:false,
}
return task
}

const clear_Task = ()=>
    {
        const tasks = document.querySelectorAll(".task")
           tasks.forEach(tasks=> tasks.remove())
    }









const button_add = document.getElementById("add")
button_add.addEventListener("click",()=>{
    const new_Task = Add_Task();
    Tasks.push(new_Task)
    console.log(new_Task);
    
})


// const button_Delete = document.getElementsByClassName("delete")

// button_Delete.addEventListener("click",()=>{
//     clear_Task()
// })
