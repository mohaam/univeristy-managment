document.addEventListener('DOMContentLoaded',function(){

        document.querySelectorAll('#change').forEach(cell =>{
        cell.onclick =()=> {
            newinfo = prompt('Enter the new information');
            if(newinfo !=null)
                {
                    request = new XMLHttpRequest();
                     request.open('POST','/department_ajax');
                    request.onload=function()
                    {
                        document.location = document.location;

                    }
                    data_send = new FormData();
                    
                    data_send.append('depname',cell.dataset.key);
                    data_send.append('what',cell.dataset.info);
                    
                    data_send.append('newinfo',newinfo);

                    request.send(data_send);
                }
        }
    });

});