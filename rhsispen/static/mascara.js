django.jQuery(function() {
    django.jQuery('.mask-cpf').mask('000.000.000-00', { reverse: true });
    django.jQuery('.mask-cep').mask('00000-000');
    django.jQuery('.mask-dt').mask('00/00/0000');
    django.jQuery('.mask-contato').mask('(00)90000-0000', { reverse: true});
    //django.jQuery('.mask-contato').mask(SPMaskBehavior, spOptions); 
    //ANTES DE SALVAR NO BD, DEVE-SE TIRAR O MASK DAS LINHAS
    django.jQuery('#servidor_form').submit(function() {
        django.jQuery('#servidor_form').find(":input[class='mask-cpf']").unmask();
        django.jQuery('#servidor_form').find(":input[class='mask-cep']").unmask();
        django.jQuery('#servidor_form').find(":input[class='mask-contato']").unmask();
        // django.jQuery('#servidor_form').find(":input[class='mask-dt_nasc']").unmask();
    });
    django.jQuery('.mask-hr').mask('00:00');
    django.jQuery('.mask-dt').datepicker({ dateFormat: "dd/mm/yy" });

});

$(function() {
    django.jQuery('.mask-dt').mask('00/00/0000');
    django.jQuery('.mask-hr').mask('00:00');
    django.jQuery('.mask-dt').datepicker({ dateFormat: "dd/mm/yy" });
});