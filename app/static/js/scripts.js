$(document).ready(function() {
     if ($("#type").val()=='Single'){
      $("#2").show();
      $("#3").hide();
      $("#4").hide();
      $("#orderby").hide();
      $('label[for="orderby"]').hide();
      $("#6").hide();
     }
     if ($("#type").val()=='Insert'){
     $("#3").show();
     $("#2").show();
     $("#4").show();
     $("#6").hide();

     }

    if ($("#type").val()=='CSVtoDB'){
     $("#6").show();
     $("#2").hide();
     $("#4").hide();
     $("#3").show();
     $("#6").show();

     }



     if ($("#Inserttype").val()=='InsertDirectly'){
    $("#5").show();
     }
     if ($("#Inserttype").val()=='InsertDirectly'){
     $("#5").hide();
     }
     if($("#type").val()=='Loop')
          {
                $("#3").show();
                 $("#2").show();
                  $("#5").hide();
                  $("#tocolumns").hide();
                  $('label[for="tocolumns"]').hide();
                  $('label[for="Inserttype"]').hide();
                  $("#4").hide();
                  $("#6").hide();


           }


     $("#type").change(function () {
     var selectedType = $(this).children("option:selected").val();

     if(selectedType=='Single')
          {     $("#6").hide();
                $("#2").show();
                 $("#3").hide();
                  $("#5").hide();
                  $("#4").hide();
                  $("#orderby").hide();
                  $('label[for="orderby"]').hide();
           }
         if(selectedType=='CSVtoDB')
          {     $("#6").show();
                $("#3").show();
                $("#2").hide();
                 $("#3").hide();
                  $("#5").hide();
                  $("#4").hide();
                  $("#orderby").hide();
                  $('label[for="orderby"]').hide();
           }

     if(selectedType=='Insert')
          {
                $("#3").show();
                 $("#2").show();
                 $("#6").hide();

           }
           if(selectedType=='Loop')
          {
                $("#3").show();
                 $("#2").show();
                  $("#5").hide();
                  $("#4").hide();
                  $("#tocolumns").hide();
                  $('label[for="tocolumns"]').hide();
                  $('label[for="Inserttype"]').hide();
                  $("#6").hide();



           }

 });
      $("#Inserttype").change(function () {
     var selectedType = $(this).children("option:selected").val();

     if(selectedType=='UpdateIfExists')
          {
                $("#5").show();

           }
     if(selectedType=='InsertDirectly')
          {
                $("#5").hide();

           }
 });

 });