let search_form=document.getElementById('search_form')
let page_links=document.getElementsByClassName('page-link')

// ensuring search-form exists, else don't need to do the following
if(search_form){
    for(let i=0; page_links.length > i; i++){
        page_links[i].addEventListener(
            'click',function(e){
            e.preventDefault()

            let page_no=this.dataset.page_no
            

            search_form.innerHTML+=`<input value=${page_no} name="page_no" hidden />`

            search_form.submit()
        }
        )
    }
}

let tags = document.getElementsByClassName('project-tag')
        for (let i=0;i<tags.length;i++){
            tags[i].addEventListener('click',(e)=>{
                let tag_id= e.target.dataset.tag
                let project_id= e.target.dataset.project
                
                fetch('http://127.0.0.1:8000/api/remove-tag/',{
                    method:'DELETE',
                    headers:{
                        'Content-Type':'application/json'
                    },
                    body:JSON.stringify({'project':project_id,'tag':tag_id})
                }).then(response => response.json())
                .then(data=>{
                    e.target.remove()
                })
            }
            )
        }