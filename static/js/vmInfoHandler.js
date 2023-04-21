(function($) {
    "use strict";
    $(document).ready(function() {
        $('.destroy-machine-bgbtn').addClass('disabled');
        $('.destroy-machine').prop('disabled', true);

        //hide loader
        $('.loader').addClass('hidden');
        // show loader with fade effect
        setTimeout(() => {
            $('.loader').removeClass('hidden');        
        }, 500);


        if (window.location.pathname == '/vminfo') {
            // get url information to know which machine to create
            $.urlParam = function(name) {
                var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
                if (results == null) {
                return null;
                }
                else {
                return decodeURI(results[1]) || 0;
                }
            }
           
            var vm = $.urlParam('vm');

            
            var isRequestPending = false;

            if (vm) {
                if (!isRequestPending) {
                    $.get(`/create-${vm}-vm`, function(data) {
                        $('.destroy-machine-bgbtn').removeClass('disabled');
                        $('.destroy-machine').prop('disabled', false);
                        console.log(data);
                        isRequestPending = true;
                        
                        // show vm info if available or print error message
                        if (data.includes('"name":')) {
                            $('.loader').addClass('hidden');
                            $('.vm-info').removeClass('hidden'); 
                            setTimeout(() => {
                                $('.loader').css('display', 'none');
                            }, 2000)

                            // affichage des infos vm dans les chaps prévus
                            const startIndex = data.indexOf('{');
                            const endIndex = data.lastIndexOf('}') + 1;
                            const vmInfoJson = data.substring(startIndex, endIndex);

                            const vmInfoObject = JSON.parse(vmInfoJson);
                            for (const info in vmInfoObject) {
                                $('#' + info +' .value').text(vmInfoObject[info]);
                            }
                        }
                    });


                    // code provisoire simulation d'animation d'attente car la conf de la transmission en temps réel prend trop de temps...
                    let i = 0;
                    const textValues = [
                        'Create Ressource group...', 
                        'Create Vnet...', 
                        'Create Subnet...', 
                        'Create Public IP address...', 
                        'Create NIC with public IP configuration...',
                        'Create Network Security Group...',
                        'Associate NSG with network interface...',
                        'Creating Virtual Machine...',
                        'Tag Virtual Machine...',
                        'Create (empty) managed Data Disk...',
                        'Get Virtual Machine by Name...',
                        'Attach Data Disk...',
                        'we are configuring the machine... it will soon be available...'
                    ]
                    let iterate = setInterval(() => {
                        $('.loading-text').text(textValues[i])
                        i++
                        if (i >= textValues.length) {
                            clearInterval(iterate)
                          }
                    }, 5000)
                }
            }



            // make the HTTP request to destroy the machine
            function destroy_machine() {
                $('.destroy-machine-bgbtn').addClass('disabled');
                $('.destroy-machine').prop('disabled', true);
                $(".destroy-machine").html('Destroying machine.... please wait, this can take 2 to 4 minutes... <i class="zmdi zmdi-spinner zmdi-hc-spin"> </i> ');
                $.ajax({
                    url: '/destroy-machine',
                    type: 'POST',
                    success: function(response) {
                        console.log('Machine destroyed successfully!');
                        $('.destroy-machine').html('Machine destroyed successfully!')
                        setTimeout(() => {
                            window.location.href='/home'
                        }, 4000);
                        $('.destroy-machine-bgbtn').removeClass('disabled');
                        $('.destroy-machine').prop('disabled', false);
                    },
                    error: function(xhr, status, error) {
                        console.error('Error destroying machine:', error);
                        $('.destroy-machine').html('Error destroying machine: Refresh page and try again')
                        $('.destroy-machine-bgbtn').removeClass('disabled');
                        $('.destroy-machine').prop('disabled', false);
                    }
                });
            }

            // destroy machine button handler

             // Listen for click events on elements with class 'destroy-machine'
            $('.destroy-machine').click(function(event) {
                event.preventDefault(); // Prevent default link behavior
                // Send AJAX request to server endpoint to destroy machine
                destroy_machine()
            });
          
        }
    });
})(jQuery);