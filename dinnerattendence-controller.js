angular.module('hiway').controller(
		'DinnerAttendenceController',
		function($scope, $mdDialog, $rootScope, API, Utils, $q,
				$timeout, $routeParams, $location) {
			$scope.bookings = [];
			function errorHandler(message) {
				return function errorHandler(response) {
					Utils.errorMessage(message, {
						status : response.status,
						message : response.data
					});
				};
			}
			
			var user = $rootScope.userId;
			$scope.runAutoSave = true;
			var dateArray = [];
			$scope.todayDate = moment().format("YYYY-MM-DD");
			$scope.today = moment().format("YYYY-MM-DD");

			/** Initialising dateArray
			 * 	dateArray contains all the dates of weekdays of that respective week
			 * */
			for (var i = 0; i < 5; i++)
			{
				dateArray[i] = moment();
			}
			
			/**
			 * prev is a function for displaying the previous week */
			$scope.prev = function(tempTodayDate) {
				tempTodayDate = moment(Utils.dateAdd(tempTodayDate,-7));
				getPrevAndNext(tempTodayDate);
			};
			
			/**
			 * next is a function for displaying the next week */
			$scope.next = function(tempTodayDate){
				tempTodayDate = moment(Utils.dateAdd(tempTodayDate,7));
				getPrevAndNext(tempTodayDate);
			};
			
			var getPrevAndNext = function(tempTodayDate){
				getMonday(tempTodayDate);
				dateUpdate(tempTodayDate);
				$scope.dinnerAttendanceWeek = [];
				createDinnerAttendanceWeek(dateArray);
				disablePastDays(dateArray);
				getDinnerAttendanceEntries();
			};
			
			/**
			 * Calculating dateArray[0] i.e.., date of monday using the below function.
			 * Based on that calculating remaining days*/
			var getMonday = function(dateToday){
				sunday = moment(dateToday).startOf('week').toDate();
				dateArray[0] = moment(Utils.dateAdd(sunday,1));
			};
			
			getMonday($scope.todayDate);
			
			/**
			 * Updating the date array with respective days of the week
			 *  */
			var dateUpdate = function(dateToday){
				for (var i = 1; i < 5; i++) {
					dateArray[i] = moment(Utils.dateAdd(dateArray[0],i));
				}
			}
			dateUpdate($scope.todayDate);

			$scope.dinnerAttendanceWeek = [];
			var weekDays = [ "Sun", "Mon", "Tue", "Wed",
			                 "Thu", "Fri" ];
			var temp = {};
			var createDinnerAttendanceWeek = function(dateArray) {
				for (var i = 0; i < dateArray.length; i++) {
					temp = {
							user : $rootScope.userId,
							date : new Date(dateArray[i]),
							day_name : weekDays[dateArray[i].day()],
							is_eating : null,
							disabled : false,
					}
					$scope.dinnerAttendanceWeek.push(temp);
				}
			}
			createDinnerAttendanceWeek(dateArray);
			
			/**Function for disabling the past days i.e.., If today is tuesday user cannot submit the
			 * schedule of monday
			 */
			var today = moment();
		
			var disablePastDays = function(dateArray) {
				for (var i = 0; i < $scope.dinnerAttendanceWeek.length; i++) {
					if (Utils.dateCompare($scope.today,dateArray[i]) === 1)
						{
						$scope.dinnerAttendanceWeek[i].disabled = true;
						}	
					if(dateArray[i].date() === today.date() && dateArray[i].day() === today.day() && today.hour()>14)
					{
						$scope.dinnerAttendanceWeek[i].disabled = true;
					}
				}
			}
			
			disablePastDays(dateArray);
			/**
			 * Getting the previous details filled by the user.
			 * */
				function getDinnerAttendanceEntries(){
					var maxDate = moment().format('YYYY-MM-DD');
					var minDate = moment($scope.dinnerAttendanceWeek[0].date).format('YYYY-MM-DD'); 
					maxDate = moment(Utils.dateAdd(minDate,5)).format('YYYY-MM-DD');	
				API.getDinnerAttendanceEntries(user,minDate,maxDate).success(function(data) {
					data = data.results;
					/*
					 * data contains the information previously filled by the user.
					 * */
					var isEating = {};
					var id = {};
					var status = {};
					for(var i=0; i < data.length ; i++)
						{
							if(data[i].is_eating == false)
								isEating[data[i].date] = "No";
							if(data[i].is_eating == true)
								isEating[data[i].date] = "Yes";
							id[data[i].date] = data[i].id;
							status[data[i].date] = 'saved';
						}
					for(var i=0; i < $scope.dinnerAttendanceWeek.length ; i++)
						{
						$scope.dinnerAttendanceWeek[i].date = moment($scope.dinnerAttendanceWeek[i].date).format('YYYY-MM-DD');
						$scope.dinnerAttendanceWeek[i].is_eating = isEating[$scope.dinnerAttendanceWeek[i].date];
						$scope.dinnerAttendanceWeek[i].id = id[$scope.dinnerAttendanceWeek[i].date];
						$scope.dinnerAttendanceWeek[i].state = status[$scope.dinnerAttendanceWeek[i].date];
						}				
				});
			};
			getDinnerAttendanceEntries();
			/**
			 * 	Sending the data through API call.
			 * */
			function postEntry(entry) {
				API.saveDinnerAttendenceEntry(entry).then(function(x) {
					entry.state = 'saved';
					entry.id = x.data.id;
				},function(x){
					entry.state = 'failed'
				});
			};
			
			 function updateEntry(entry) {
		        API.updateDinnerAttendenceEntry(entry).then(function(x){
		        	entry.state = 'saved';
		        });
		    };
			
			$scope.addEntry = function(index) {
				$scope.dinnerAttendanceWeek[index].user = $rootScope.userId;
				$scope.dinnerAttendanceWeek[index].date = moment($scope.dinnerAttendanceWeek[index].date).format('YYYY-MM-DD');			
				if($scope.dinnerAttendanceWeek[index].state === "saved")
					updateEntry($scope.dinnerAttendanceWeek[index]);
				else 
					postEntry($scope.dinnerAttendanceWeek[index]);	
			};
		});