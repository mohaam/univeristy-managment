document.addEventListener('DOMContentLoaded',function(){
    document.querySelectorAll("#del").forEach(btn =>{
        btn.onclick =()=> {
             request = new XMLHttpRequest();
             request.open('POST','/program_manager_ajax');
            request.onload=function()
            {

                document.location = document.location; 
            }
            data_send = new FormData();
            data_send.append('do','delete');
            data_send.append('id',btn.dataset.id);
            data_send.append('table',btn.dataset.table);
            request.send(data_send);
        }
    });
        document.querySelectorAll('.change').forEach(cell =>{
        cell.onclick =()=> {
            newinfo = prompt('Enter the new information');
            if(newinfo !=null)
                {
                    request = new XMLHttpRequest();
                     request.open('POST','/program_manager_ajax');
                    request.onload=function()
                    {
                        data = JSON.parse(request.responseText)
                        if(data["edit"] == 1 )
                        {
                            document.location = document.location;        
                        }
                        if(data["edit"] == 0)
                        {
                            alert("enter validate data")
                        }

                    }
                    data_send = new FormData();
                    data_send.append('do','edit');
                    data_send.append('id',cell.dataset.id);
                    data_send.append('col',cell.dataset.col);
                    data_send.append('table',cell.dataset.table);
                    data_send.append('newinfo',newinfo);

                    request.send(data_send);
                }
        }
    });

});