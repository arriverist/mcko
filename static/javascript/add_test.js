function remove(){
    var last_chq_no = $('#total_chq').val();
    if(last_chq_no>1){
        $('#new_'+last_chq_no).remove();
        $('#total_chq').val(last_chq_no-1);
    }
}