var app = angular.module('fencin');

app.controller('backroomController', function ($scope, checkinService, firebaseService, $location, currentAuth) {
  console.log(currentAuth);
  if(currentAuth){
    
    $scope.getTournaments = function () {
      firebaseService.getTournaments().then(function (data) {
        $scope.tournaments = data;
        $scope.tournamentNames = [];
        for(i = 0; i < $scope.tournaments.length; i++){
          $scope.tournamentNames.push($scope.tournaments[i].tournament.tournamentName);
        }           
      });    
    }();
    
    $scope.currentTournament = checkinService.getCurrentTournament();
    if(!$scope.currentTournament){
      $location.path('/checkinSelection');
    } else {
      $scope.checkedInFencers();
    }

    //gets the checked in fencers from firebase and binds them to scope for display
    $scope.checkedInFencers = function () {
      firebaseService.getCheckedInFencers().then(function (data) { 
        $scope.fencers = data;
      });
    };

    $scope.fencingTime = function (fencer) {
      firebaseService.fencingTime(fencer);
    };

  }
});