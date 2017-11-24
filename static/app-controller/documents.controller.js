angular.module('app').controller('FileController', function ($rootScope,$route, UserService, FlashService, $uibModal, $confirm) {

    var vm = this;
    getFiles()

    vm.selectedIndex = null;
    vm.setFilter = function ($index, flt){
        vm.selectedIndex = $index;

        if (flt) {
            vm.displayedCollection = [];

            for (var i = 0; i < $rootScope.fileCollection.length; i++) {
                if (flt == $rootScope.fileCollection[i].type) {
                    vm.displayedCollection.push($rootScope.fileCollection[i])
                }
            }
        }
        else {
            vm.displayedCollection = [].concat($rootScope.fileCollection)
        }
    };

    vm.download = function(fileId, sharedBy){
        var url = "/user/"+$rootScope.globals.currentUser.username+"/file/"+fileId+"?action=df";
        if (sharedBy)
            url = url + "&shared_by="+sharedBy;

        UserService.DownloadFile(url).then(function (response) {

            if (typeof response == 'object')
                FlashService.Error(response.errorMessage);
            else
                // todo delete second download file
                document.getElementById('my_iframe').src = url;

        });
    }

    function getFiles(){
        UserService.GetFiles($route.current.params.user_id).then(function (response) {

            if (response.success){
                $rootScope.fileCollection = response.result.files;
                vm.displayedCollection = [].concat($rootScope.fileCollection);
                //$rootScope.fileExtendList = response.result.extends;
                //$rootScope.fileExtendList = ['png', 'txt', 'gif'];

                $rootScope.fileQuota = {
                    used_quota: response.result.used_quota,
                    quota: response.result.quota
                };
                $rootScope.setPercentQuota()
            }
            else {
                FlashService.Error(response.errorMessage);
            }
        });
    }

    $rootScope.setPercentQuota = function setPercentQuota(){
        $rootScope.fileQuota.percent_quota = Math.round(($rootScope.fileQuota.used_quota*100)/$rootScope.fileQuota.quota);

        $rootScope.progress_type = 'info';
        if ($rootScope.fileQuota.percent_quota > 50){
            $rootScope.progress_type = 'warning'
        }
        if ($rootScope.fileQuota.percent_quota > 90){
            $rootScope.progress_type = 'danger'
        }
    };

    vm.removeItem = function removeItem(row) {
        var index = $rootScope.fileCollection.indexOf(row);
        if (index !== -1) {

            $confirm({text: 'Are you sure you want to delete?', ok: 'Yes', cancel: 'No'})
                .then(function() {
                    UserService.deleteFile(row.id).then(function (response) {
                        if (response.success){
                            $rootScope.fileCollection.splice(index, 1);


                            // todo update fileExtend
                            $rootScope.fileQuota.used_quota = $rootScope.fileQuota.used_quota - row.size;
                            $rootScope.setPercentQuota()
                        }
                        else
                            FlashService.Error(response.errorMessage);
                    });
                });
        }
    };

    // create shared modal form
    vm.openShare = function openShare(FileObj) {
        var modalShareInstance = $uibModal.open({
            animation: true,
            templateUrl: 'ModalShareContent.html',
            controller: 'ModalInstanceCtrl',
            resolve: {
                FileObj: function () {
                    return FileObj;
                }
            }
        });

        modalShareInstance.result.then(function (model) {
            console.log(model)
        }, function () {});
    };

    // create upload modal form
    vm.openUpload = function openUpload() {
        var modalUploadInstance = $uibModal.open({
            animation: true,
            templateUrl: 'ModalUploadContent.html',
            controller: 'ModalInstanceCtrl',
            size: 'lg',
            resolve: {
               FileObj: function () {
                    return {};
                }
            }
        });

        modalUploadInstance.result.then(function () {}, function () {
            $rootScope.uploader.clearQueue();
        });
    };
});

// controller for modal forms
angular.module('app').controller('ModalInstanceCtrl', function ($rootScope, FlashService, $filter, $uibModalInstance, UserService, FileObj) {

    // generate upload modal
    if (Object.keys(FileObj).length == 0) {
        UserService.uploadFile();
        var uploader = $rootScope.uploader;

        uploader.filters.push({
            name: 'customFilter',
            fn: function(item /*{File|FileLikeObject}*/, options) {
                return this.queue.length < 5;
            }
        });

        $rootScope.cancelUpload = function () {
            uploader.clearQueue();
            $uibModalInstance.dismiss('cancel');
        };
        uploader.onSuccessItem = function (fileItem, response, status, headers) {

            if (!response.success) {
                fileItem.isError = true;
                fileItem.isSuccess = false;
                fileItem.errorMessage = response.errorMessage;
            }
            else {
                var ext = fileItem._file.type.split('/').pop();

                $rootScope.fileCollection.push({
                    date_load: $filter('date')(new Date(), 'dd-MM-yyyy HH:mm', $rootScope.globals.local),
                    id: response.id,
                    name: fileItem._file.name,
                    size: fileItem._file.size,
                    type: ext
                });
                $rootScope.fileQuota.used_quota = $rootScope.fileQuota.used_quota + fileItem._file.size;
                $rootScope.setPercentQuota();
                //$rootScope.fileExtendList.push(ext)
            }
        };
    }
    // generate share modal
    else {
        $rootScope.shareFile = FileObj;
        $rootScope.shareList = [];
        $rootScope.friendList = [];

        var initShare = function() {

            UserService.getFileShare(FileObj.id).then(function (response) {
                if (response.success){
                    $rootScope.friendList = response.friend_list;
                    $rootScope.shareList = response.shared_list;
                }
                else
                    FlashService.Error(response.errorMessage);
            });
        };

        $rootScope.settings = {
          filterClear: 'Show all!',
          filterPlaceHolder: 'Filter!',
          moveSelectedLabel: 'Move selected only',
          moveAllLabel: 'Move all!',
          removeSelectedLabel: 'Remove selected only',
          removeAllLabel: 'Remove all!',
          moveOnSelect: false,
          preserveSelection: 'moved',
          postfix: '_helperz',
          selectMinHeight: 130,
          filter: true,
          infoAll: 'Showing all {0}!',
          infoFiltered: '<span class="label label-warning">Filtered</span> {0} from {1}!',
          infoEmpty: 'Empty list!',
          filterValues: true
        };

        initShare();

        $rootScope.okShare = function (selectedShare, form) {
            var data = {shared_list: selectedShare,
                        file_name: $rootScope.shareFile.name
            };

            UserService.setFileShare(FileObj.id, data).then(function (response) {
                if (response.success)
                    form.$setPristine();
                else
                    FlashService.Error(response.errorMessage);
            });
        };

        $rootScope.cancelShare = function () {
            $uibModalInstance.dismiss('cancel');
        };
    }
});

// FILTER
angular.module('app').filter('bytes', function() {
	return function(bytes, precision) {
		if (isNaN(parseFloat(bytes)) || !isFinite(bytes)) return '-';
		if (typeof precision === 'undefined') precision = 1;
		var units = ['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'],
			number = Math.floor(Math.log(bytes) / Math.log(1024));
		return (bytes / Math.pow(1024, Math.floor(number))).toFixed(precision) +  ' ' + units[number];
	}
});