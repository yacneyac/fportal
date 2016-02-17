(function () {
    'use strict';

    angular
        .module('app')
        .controller('Picture', function($rootScope, UserService, FlashService) {

            $rootScope.Image='';
            $rootScope.CroppedImage='';
            $rootScope.AvatarLoading = false;

            var handleFileSelect=function(evt) {
                var file = evt.currentTarget.files[0];
                var reader = new FileReader();
                reader.onload = function (evt) {
                    $rootScope.$apply(function($rootScope){
                        $rootScope.Image = evt.target.result;
                    });
                };
                reader.readAsDataURL(file);
                $rootScope.filename = file.name;
                $rootScope.filentype = file.type.split('/')[1];
            };

            angular.element(document.querySelector('#fileInput')).on('change', handleFileSelect);

            $rootScope.changePicture = function (form){
                var image = angular.element(document.querySelector('#pict'));
                var imageBase64 = image[0].src;
                var filename = 'avatar_' + (Math.floor(Math.random() * 10) +1 )+ '.' + $rootScope.filentype;

                var fileObj = {
                    'file': {
                        'name': filename,
                        'body': imageBase64.split(',')[1]
                    }
                };

                UserService.ChangePicture(fileObj).then(function (response) {
                    $rootScope.AvatarLoading = true;
                    form.$invalid = true;
                    $('#fileInput').val('');
                    delete $rootScope.Image;
                    delete $rootScope.CroppedImage;

                    if (response.success){
                        $rootScope.AvatarLoading = false;
                        $rootScope.user.avatarurl = '/static/avatar/' + $rootScope.user.id + '/'+ filename;
                        FlashService.Success('Updated!');
                    }
                    else {
                        $rootScope.AvatarLoading = false;
                        FlashService.Error(response.errorMessage);
                    }
                });
            };
          })
        .directive('validFile',function(){
            return {
                require:'ngModel',
                link:function(scope,el,attrs,ngModel){
                    //change event is fired when file is selected
                    el.bind('change',function(){
                        scope.$apply(function(){
                            ngModel.$setViewValue(el.val());
                            ngModel.$render();
                        })
                    })
                }
            }
        })
})();
