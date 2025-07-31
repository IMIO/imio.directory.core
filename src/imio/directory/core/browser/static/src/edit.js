// window.addEventListener('unhandledrejection', event => {
//     if (event.reason && event.reason.name === 'ChunkLoadError') {
//         console.warn('Chunk load failed, but on s’en fout.');
//         event.preventDefault(); // empêche l’erreur d’être affichée
//     }
// });

$(document).ready(function() {
    ///////////////////////////////////////////////////////////////
    // Titre principal : "Horaire"
    ///////////////////////////////////////////////////////////////
    var $titleMultiSchedule = $('#fieldsetlegend-multischedule');
    $titleMultiSchedule.text("Horaire");
    ///////////////////////////////////////////////////////////////
    // Titre du 1er horaire = "Horaire standard"
    ///////////////////////////////////////////////////////////////
    var $titleHoraireStandard = $('#fieldset-multischedule > div.row:first > div:first > label:first');
    $titleHoraireStandard.text("Horaire standard");

    var $titleHoraireParticulier = $('#fieldset-multischedule > div.row:first > div:not(:first) > label:first');
    $titleHoraireParticulier.text("Horaire particulier");

    ///////////////////////////////////////////////////////////////
    // Modifier le texte du bouton "Ajouter" en "Ajouter un horaire particulier"
    ///////////////////////////////////////////////////////////////
    var $addScheduleButton = $('#form-widgets-IMultiScheduledContent-multi_schedule-buttons-add');

    // Vérifier si le texte du bouton contient "Ajouter" et le changer
    var buttonText = $addScheduleButton.text();
    if (buttonText.includes("Ajouter")) {
        $addScheduleButton.text("Ajouter un nouvel horaire particulier");
    }

    ///////////////////////////////////////////////////////////////
    // Modifier le texte du bouton "Supprimer" en "Supprimer la dernière plage de dates"
    ///////////////////////////////////////////////////////////////
    var $PlageDeDateDelButton = $('[id^="form-widgets-IMultiScheduledContent-multi_schedule-"][id$="-widgets-dates-buttons-remove"]');
    $PlageDeDateDelButton.text("Supprimer la dernière plage de dates");



    ///////////////////////////////////////////////////////////////
    // Gestion de l'événement click pour le bouton "Ajouter un horaire particulier"
    ///////////////////////////////////////////////////////////////
    $addScheduleButton.on('click', function() {

        // Vérifier si un type de contact a été sélectionné
        var isContactTypeSelected = $('#formfield-form-widgets-type input:checked').length > 0;
        if (!isContactTypeSelected) {
            alert("Veuillez choisir un type de contact avant d'ajouter un horaire particulier.");
            $(window).scrollTop(0); // Remonter en haut de la page
            return false; // Annuler l'action du clic
        }

        // Vérifier si un titre a été saisi
        var contactTitle = $('#form-widgets-IBasic-title').val();
        if (contactTitle.length === 0) {
            alert("Veuillez entrer un titre à votre contact avant d'ajouter un horaire particulier.");
            $(window).scrollTop(0); // Remonter en haut de la page
            return false; // Annuler l'action du clic
        }

    });

    /////////////////////////////////////////////////////////////////////////////////////////////
    // Modifier le texte du bouton "Ajouter" (relatif aux dates) en "Ajouter une plage de dates"
    /////////////////////////////////////////////////////////////////////////////////////////////
    $('[id^="form-widgets-IMultiScheduledContent-multi_schedule-"][id$="-widgets-dates-buttons-add"]').each(function() {
        if ($(this).text().indexOf("Ajouter") !== -1) {
            $(this).text('Ajouter une nouvelle plage de dates');
        }
    });

    /////////////////////////////////////////////////////////////////////////////////////////////
    // Si on détecte un champ de type multi-widget, on déploie le fieldset
    /////////////////////////////////////////////////////////////////////////////////////////////
    if ($(".multi-widget-field").length > 0){
        $('#fieldsetlegend-multischedule').trigger('click');
    }

    ///////////////////////////////////////////////////////////////
    // Pour chaque "horaire particulier" on met un titre par défaut
    ///////////////////////////////////////////////////////////////    
    var cpt = 0;
    $("div.multi-widget").find("div.multi-widget-field").each(function(index) {        
        var $this = $(this);
        if ($this.attr("id") == "formfield-form-widgets-IMultiScheduledContent-multi_schedule-"+cpt) {            
            $(this).css('padding', '2em');
            $(this).css('border', '1px solid #ccc');
            if (cpt % 2 === 0) {
                // Couleur pour les éléments d'index pair
                $(this).css('background-color', '#f2f2f2'); // Exemple de gris clair
            } else {
                // Couleur pour les éléments d'index impair
                $(this).css('background-color', '#ffffff'); // Exemple de blanc
            }          
            $this.find(".invalid-feedback").hide(); // cache les messages d'erreur
            // cache les checkboxes qui empêchent le delete
            $(this).find('input[type="checkbox"]').hide();
            $this.find("textarea").val("Horaire particulier " + (cpt + 1));
            $(this).find('label[for="form-widgets-IMultiScheduledContent-multi_schedule-'+cpt+'-widgets-dates"]').hide();
            var $label = $this.find("label").first();
            var currentText = $label.text();
            $label.text("Horaire particulier numéro " + currentText);
            $(this).find('input[type="checkbox"]')             // Sélectionne la checkbox
            .parent()                                      // Va jusqu'au parent de la checkbox
            .find("label")                                 // Sélectionne le label associé
            .find("span")                                  // Sélectionne le span sous le label
            .each(function() {                             // Itère sur chaque span trouvé
                var currentText = $(this).text();           // Récupère le texte actuel du span
                if (currentText.trim() !== "") {            // Si le texte du span n'est pas vide
                    $(this).text("Plage de dates numéro " + currentText); // Préfixe le texte avec le texte désiré
                }
            });
            cpt = cpt + 1;
        }        
    });

    // Ici, on essaie d'activer automatiquement la 1ere plage de dates
    var $container_particularSchedule = $(".multi-widget")
    var cpt = 0;
    $container_particularSchedule.find('div[class*="kssattr-fieldname-form.widgets.IMultiScheduledContent.multi_schedule."][class$=".widgets.dates"]').each(function(index) {
        var $this = $(this);
        // console.log("blabla1 = " + "formfield-form-widgets-IMultiScheduledContent-multi_schedule-"+cpt+"-widgets-dates");
        // console.log("blabla2 = " + $this.attr("id"));
        if ($this.attr("id") == "formfield-form-widgets-IMultiScheduledContent-multi_schedule-"+cpt+"-widgets-dates") {
            // console.log("KAMOULOX");
            $date_picker = $this.find(".pat-date-picker");
            if ($date_picker.length == 0){
                // console.log("PAS DE DATE PICKER");
                var $lenght = $this.find('button[value="Ajouter"]').length
                // console.log("LENGHT = " + $lenght);
                var $button = $this.find('button[value="Ajouter"]')
                // $button.click();
                // try {
                //     var button = $button.get(0);
                //     button.dispatchEvent(new MouseEvent('click', {
                //         bubbles: true,
                //         cancelable: true,
                //         view: window
                //     }));
                // } catch (e) {
                //     // console.error("Erreur lors du clic programmatique :", e);
                // }                               
                // $this.find('button[value="Ajouter"]').click();
                $this.find('button[id*="form-widgets-IMultiScheduledContent-multi_schedule-"][id$="dates-buttons-add"]').click();
            }
            cpt = cpt + 1;
        }
    });

    if ($container_particularSchedule.length > 0){
        remove_dates_buttons = $('[id*="multi_schedule-"][id$="dates-buttons-remove"]');
        remove_dates_buttons.on('click', function() {
            // 'this' fait référence au bouton sur lequel l'utilisateur a cliqué
            var $clickedButton = $(this);
            var $container = $(this).parent();
            var $checkbox_to_delete = $container.prev().find('input[type="checkbox"]');
            var $start_date_field = $container.prev().find('input[name$="widgets.start_date"]');
            $start_date_field.val('');
            var $end_date_field = $container.prev().find('input[name$="widgets.end_date"]');
            $end_date_field.val('');
            $checkbox_to_delete.prop('checked', true);
        });

        remove_schedule_button = $("#form-widgets-IMultiScheduledContent-multi_schedule-buttons-remove");
        remove_schedule_button.text("Supprimer le dernier horaire particulier");
        remove_schedule_button.on('click', function() {
            var $container = $(this).parent();
            var $checkbox_to_delete = $container.prev().find('input[type="checkbox"]').first();
            $checkbox_to_delete.prop('checked', true);
        });
    }    

    /////////////////////////////////////////////////////////////////////////////////////////////
    // GESTION DE LA FERMETURE EXCEPTIONNELLE
    /////////////////////////////////////////////////////////////////////////////////////////////

    // On cache la case à cocher dans fermeture exceptionnelle.
    $ExceptionalCloseDateCheckbox = $('[id^="form-widgets-IExceptionalClosureContent-exceptional_closure-"][id$="-remove"][type="checkbox"]');
    $ExceptionalCloseDateCheckbox.hide();

    // On cache les numéros qui traînent dans la fermeture exceptionnelle
    var $labels = $('div[id^="formfield-form-widgets-IExceptionalClosureContent-exceptional_closure-"] .multi-widget-number');
    $labels.hide();

    // On renomme le bouton d'ajout
    $ExceptionalClose = $('#form-widgets-IExceptionalClosureContent-exceptional_closure-buttons-add');
    $ExceptionalClose.text("Ajouter une autre fermeture exceptionnelle");
    $ExceptionalClose.on('click', function() {
        // Logique pour ajouter une autre fermeture exceptionnelle
    });

    // On renomme le bouton de suppression
    $ExceptionalCloseDelButton = $('#form-widgets-IExceptionalClosureContent-exceptional_closure-buttons-remove');
    $ExceptionalCloseDelButton.text("Supprimer la dernière fermeture exceptionnelle");

    // On gère la suppression qui dépend de la sélection de la checkbox précédemment cachée
    // (on auto-check la checkbox et on vide les champs)
    $ExceptionalCloseDelButton.on('click', function() {
        // Logique pour supprimer la dernière fermeture exceptionnelle
        var $clickedButton = $(this);
        var $container = $(this).parent();
        var $checkbox_to_delete = $container.prev().find('input[type="checkbox"]');
        var $start_date_field = $container.prev().find('input[name$="form.widgets.IExceptionalClosureContent.exceptional_closure"][type="date"]');
        $start_date_field.val('');
        var $title_field = $container.prev().find('input[name$="form.widgets.IExceptionalClosureContent.exceptional_closure"][type="textarea"]');
        $title_field.val('');
        $checkbox_to_delete.prop('checked', true);
    });
});