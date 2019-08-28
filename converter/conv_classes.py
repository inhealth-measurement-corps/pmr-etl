import matplotlib 
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, date, timedelta, timezone
import calendar 
from scipy.stats import linregress

class Patient(object):

    # The class "constructor" - It's actually an initializer 
    def __init__(self, mrn, rn, bn, admission_date, transfer_date, discharge_date, length_of_stay):
        self.mrn = mrn # MRN number (possibly same as patient number?)
        self.rn = rn # Room number, the patients deduced room number. We don't know it yet.
        self.bn = bn  # Badge number - the number/id of the badge they're wearing
        self.admission_date = admission_date
        self.transfer_date = transfer_date #Date of transfer from PCU? Or this field only relevant for PCU?
        self.discharge_date = discharge_date #Date of discharge? 
        self.length_of_stay = length_of_stay # need to decide if we want this to be a number, string, datetime object, or what

        self.ambulations = [] # All the ambulations the patients made
        self.ambulations_per_day = {} # map from day to number of ambulations in that day
        #TO-DO: self.ambulation_per_day is probably redundant, given we have self.date_to_day. 
        #Get rid of it and shift things that are reliant on it (compliance) to rely on date_to_day


        self.date_to_day = {} # map from date to Day objects

        self.total_distance = 0

        self.num_ambulations = 0 # the number of ambulations they made
        self.avg_num_ambulations = 0 # average number of ambulations per day

        self.compliance_1_num = 0 # number of days they do 1 ambulation
        self.compliance_2_num = 0 # same as above but 2
        self.compliance_3_num = 0 # 3

        self.compliance_1 = 0.0 #percent of days they do 1 ambulation
        self.compliance_2 = 0.0 #do two
        self.compliance_3 = 0.0 # do three

        self.max_dur = -1 #max ambulation duration
        self.mean_dur = -1
        self.min_dur = -1

        self.max_dist = -1 #max ambulation distance
        self.mean_dist = -1
        self.min_dist = -1

        self.max_speed = -1 #max ambulation speed
        self.mean_speed = -1
        self.min_speed = -1

        self.delta_dist = 0 #change in distance over time (slope of linear regression?)
        self.delta_dur = 0
        self.delta_speed = 0

        self.ambulation_time_list = [] #a list of the start times of each ambulation
        self.dur_list = [] # a list of the duration of each ambulation, matching the list o start times (i.e. same index will correspond to same ambulation)
        self.dist_list = [] # same as above but for distance
        self.speed_list = [] # same as above but for speed

        self.dyn_update = False #whether we run adjust_data automatically when an ambulation is added, or only when requested

        self.generate_day_map()


    def add_ambulation(self, ambulation):
        self.ambulations.append(ambulation)

        self.mean_dist = self.add_to_mean(self.mean_dist, self.num_ambulations, ambulation.dist)
        self.mean_dur = self.add_to_mean(self.mean_dur, self.num_ambulations, ambulation.dur)
        self.mean_speed = self.add_to_mean(self.mean_speed, self.num_ambulations, ambulation.speed)

        self.max_dist = max(self.max_dist, ambulation.dist)
        self.max_dur = max(self.max_dur, ambulation.dur)
        self.max_speed = max(self.max_speed, ambulation.speed)

        self.min_dist = self.update_min(self.min_dist, ambulation.dist)
        self.min_dur = self.update_min(self.min_dur, ambulation.dur)
        self.min_speed = self.update_min(self.min_speed, ambulation.speed)

        #! just added
        self.total_distance += ambulation.dist

        self.num_ambulations += 1
        date_string = str(ambulation.start_date) #get the date the ambulation occured

        d1 = date(ambulation.start_date.year, ambulation.start_date.month, ambulation.start_date.day)
        if self.ambulations_per_day.get(date_string) != None: #there has already been an ambulation on this date
            self.ambulations_per_day[date_string] = self.ambulations_per_day.get(date_string) + 1;

        else: #this is the first ambulation on this day 
            self.ambulations_per_day[date_string] = 1 
        
        if self.date_to_day.get(d1) != None: #there has already been an ambulation on this date, and this Day exists
            day = self.date_to_day[d1] #get the Day object corresponding to this date
            day.add_ambulation(ambulation)

        else: #this day is not in our map
            print("Error: Day is not already in map")
            print("Problem patient:", self.mrn)
        
        #self.adjust_data()
        self.calc_compliances()


        if self.dyn_update:
            self.adjust_data()

    def adjust_data(self): # adjusts various data members that are based on the ambulation data
        self.calc_avg_num_ambs() 
        self.calc_compliances()
        self.generate_lists()
        
    def add_to_mean(self, prev_mean, prev_size, value): # prev_mean and prev_size are the mean and size before this insertion
        if prev_size == 0: #this is the first ambulation being entered, so the mean is just the value
            return value
        else:
            return (prev_size * prev_mean + value) / (prev_size + 1) #lets us update a mean in O(1) time

    def update_min(self, curr_value, value): #curr_value is the current value of whatever we are passing in (i.e. min_dist, min_dur, min_speed)
        if self.num_ambulations == 0:
            return value
        else:
            return min(curr_value, value)

    def calc_avg_num_ambs(self):
        total = 0
        for key, val in self.ambulations_per_day.items():
            total += val

        self.avg_num_ambulations = total/len(self.ambulations_per_day)

    def test_date_stuff(self):
        delta = self.discharge_date - self.transfer_date
        for i in range(delta.days + 1):
            print(self.transfer_date + timedelta(i))

    def generate_day_map(self):
        delta = self.discharge_date - self.transfer_date
        for i in range(delta.days + 1):
            date = self.transfer_date + timedelta(i)
            day = Day(date, i + 1)
            self.date_to_day[date] = day

        sorted(self.date_to_day)
        '''
        for x, y in self.date_to_day.items():
            print("date:", x, "Day object:", y)
        '''

    #!! just added
    #we run through the map of each day to number of ambulations to find the number of days they comply with 
    #each one then calculate the percentage of the time they comply in general based off of it 
    def calc_compliances(self):
        self.compliance_1_num = 0 # avoid recounting each time
        self.compliance_2_num = 0
        self.compliance_3_num = 0
        for key, val in self.ambulations_per_day.items():
            if val >= 1:
                self.compliance_1_num+=1
            if val >= 2:
                self.compliance_2_num+=1
            if val >= 3:
                self.compliance_3_num+=1

        self.compliance_1 = self.compliance_1_num/self.length_of_stay
        self.compliance_2 = self.compliance_2_num/self.length_of_stay
        self.compliance_3 = self.compliance_3_num/self.length_of_stay

        #some work to make it be in percentage form rounded to 2 decimals
        self.compliance_1 *= 100
        self.compliance_2 *= 100
        self.compliance_3 *= 100

        self.compliance_1 = round(self.compliance_1, 2)
        self.compliance_2 = round(self.compliance_2, 2)
        self.compliance_3 = round(self.compliance_3, 2)

    def print_days(self):
        for x, y in self.date_to_day.items():
            print()
            print("Info for day", x)
            print("# of ambulations:", y.num_ambulations)
            print("Duration Info-", "max:", y.max_dur, "min:", y.min_dur, "mean:", y.mean_dur)
            print("Distance Info-", "max:", y.max_dist, "min:", y.min_dist, "mean:", y.mean_dist)
            print("Speed Info-", "max:", y.max_speed, "min:", y.min_speed, "mean:", y.mean_speed)

    #only using days with regressions in the calculation
    def regression_v1(self):
        self.generate_lists_v1()
        if len(self.ambulation_time_list) > 1: #need to have more than one ambulation to run the regression
            self.calc_deltas()

    #treating days with no ambulations as having 1 ambulation with 0 duration, 0 distance, 0 speed
    def regression_v2(self):
        self.generate_lists_v2()
        if len(self.ambulation_time_list) > 1: #need to have more than one ambulation to run the regression
            self.calc_deltas()

    #treating days with no ambulations as having 1 ambulation with 0 duration, 0 distance, 0 speed
    def regression_v3(self):
        if len(self.ambulations) > 1: #need to have more than one ambulation to run the regression
            self.calc_deltas_w_amb_num()


    def calc_deltas(self):
        #print(type(self.ambulation_time_list))
        print(type(self.ambulation_time_list[0]))
        slope, intercept, r_value, p_value, std_err = linregress(self.ambulation_time_list, self.dist_list)
        #self.plot_regression(slope, intercept, r_value, p_value, std_err, np.asarray(self.ambulation_time_list), np.asarray(self.dist_list))
        self.delta_dist = slope
        slope, intercept, r_value, p_value, std_err = linregress(self.ambulation_time_list, self.dur_list)
        self.delta_dur = slope
        slope, intercept, r_value, p_value, std_err = linregress(self.ambulation_time_list, self.speed_list)
        self.delta_speed = slope

    def calc_deltas_w_amb_num(self):
        self.sort_ambulations()
        num_list = range(1, len(self.ambulations) + 1)
        print(num_list)
        for ambulation in self.ambulations:
            self.dur_list.append(ambulation.dur)
            self.dist_list.append(ambulation.dist)
            self.speed_list.append(ambulation.speed)

        #print("length of num_list:", len(num_list), "length of other lists:", len(self.dur_list), len(self.dist_list), len(self.speed_list))
        
        slope, intercept, r_value, p_value, std_err = linregress(num_list, self.dist_list)
        #self.plot_regression(slope, intercept, r_value, p_value, std_err, np.asarray(num_list), np.asarray(self.dist_list))
        self.delta_dist = slope
        slope, intercept, r_value, p_value, std_err = linregress(num_list, self.dur_list)
        self.delta_dur = slope
        slope, intercept, r_value, p_value, std_err = linregress(num_list, self.speed_list)
        self.delta_speed = slope
        


    def plot_regression(self, slope, intercept, r_value, p_value, std_err, x, y):
        plt.plot(x, y, 'o', label='original data')
        plt.plot(x, intercept + slope*x, 'r', label='y={:.6f}x+{:.6f}'.format(slope,intercept))
        #label='y={:.2f}x+{:.2f}'.format(slope,intercept)
        #plt.title('$y=%3.7sx+%3.7s$'%(slope, intercept))
        #plt.title("Patient", self.mrn)
        plt.title('Patient %s'%(self.mrn))
        plt.legend()
        plt.show()
        plt.close()

    def generate_lists_v1(self):
        for ambulation in self.ambulations:
            #converting the date to seconds since 1/1/1970. Done so we can calculate change over time in seconds
            DAY = 24*60*60 # POSIX day in seconds (exact value)
            timestamp = (ambulation.start_date.toordinal() - date(1970, 1, 1).toordinal()) * DAY
            timestamp = (ambulation.start_date - date(1970, 1, 1)).days * DAY
            #timestamp /= 1000000000
            
            transfer_time = (self.transfer_date.toordinal() - date(1970, 1, 1).toordinal()) * DAY
            transfer_time = (self.transfer_date - date(1970, 1, 1)).days * DAY
            timestamp -= transfer_time #getting time relative to transfer date

            
            if ambulation.start_time != None:
                start_time = datetime.strptime(ambulation.start_time[:-8], "%H:%M:%S").time()
                timestamp += start_time.total_seconds()

            
            self.ambulation_time_list.append(timestamp)
            self.dur_list.append(ambulation.dur)
            self.dist_list.append(ambulation.dist)
            self.speed_list.append(ambulation.speed)
            
        #self.normalize_amb_time_list()


    def generate_lists_v2(self):
        temp_amb_list = self.ambulations.copy()
        for x, y in self.date_to_day.items():
            if y.num_ambulations == 0:
                temp_amb = Ambulation(-1, x, None, 0,0,0)
                temp_amb_list.append(temp_amb)

        for ambulation in temp_amb_list:
            #converting the date to seconds since 1/1/1970. Done so we can calculate change over time in seconds
            DAY = 24*60*60 # POSIX day in seconds (exact value)
            timestamp = (ambulation.start_date.toordinal() - date(1970, 1, 1).toordinal()) * DAY
            timestamp = (ambulation.start_date - date(1970, 1, 1)).days * DAY
            #timestamp /= 1000000000
            
            transfer_time = (self.transfer_date.toordinal() - date(1970, 1, 1).toordinal()) * DAY
            tranfer_time = (self.transfer_date - date(1970, 1, 1)).days * DAY
            timestamp -= transfer_time 

            if ambulation.start_time != None:
                timestamp += ambulation.start_time.total_seconds()
            
            self.ambulation_time_list.append(timestamp)
            self.dur_list.append(ambulation.dur)
            self.dist_list.append(ambulation.dist)
            self.speed_list.append(ambulation.speed)



    def print_list(self):
        print(self.ambulation_time_list)
        print(self.dur_list)


    def normalize_amb_time_list(self):

        for i in range(len(self.ambulation_time_list)):
            time = self.ambulation_time_list[i]
            #print(time)
            #print(time.timestamp())
            self.ambulation_time_list[i] = time.timestamp()
            print(time.timestamp())


    def show_regression(self, type):
        if type == "duration":
            plt.scatter(self.ambulation_time_list, self.dur_list)
        elif type == "distance":
            plt.scatter(self.ambulation_time_list, self.dist_list)
        elif type == "speed":
            plt.scatter(self.ambulation_time_list, self.speed_list)
        else:
            print("Input param must be duration, distance, or speed.")
        plt.ylabel("dv")
        plt.xlabel("iv")
        plt.show()

    def calculate_reg_data(self):
        np_amb_list = np.array(self.ambulation_time_list)
        np_dur_list = np.array(self.dur_list)


    def print_data(self):
        print("mrn:", self.mrn, "rn:", self.rn ,"bn:", self.bn, "# of ambulations:", self.num_ambulations, "LoS:", self.length_of_stay)
        print("Dates-", "admission date:", self.admission_date, "transfer date:", self.transfer_date, "discharge date:", self.discharge_date)
        print("Duration Info-", "max:", self.max_dur, "min:", self.min_dur, "mean:", self.mean_dur)
        print("Distance Info-", "max:", self.max_dist, "min:", self.min_dist, "mean:", self.mean_dist)
        print("Speed Info-", "max:", self.max_speed, "min:", self.min_speed, "mean:", self.mean_speed)
        print("Avg num ambulations-", self.avg_num_ambulations)
        print("Compliances-", "Compliance 1:", self.compliance_1, "Compliance 2:", self.compliance_2, "Compliance 3:", self.compliance_3)
        print("Deltas-", "Distance CoT:", self.delta_dist, "Duration CoT:", self.delta_dur, "Speed CoT:", self.delta_speed)

    #Sorts ambulations by number of ambulations
    def sort_ambulations(self):
        self.ambulations.sort(key=lambda x: x.amb_num)

    def print_ambulations(self):
        self.sort_ambulations()
        for ambulation in self.ambulations:
            ambulation.print_amb_data()
        for dist in self.dist_list:
            print(dist)


class Ambulation(object):


    # The class "constructor" - It's actually an initializer 
    def __init__(self, mrn, start_date, start_time, distance, duration, speed, ambulation_number):
        self.mrn = mrn #mrn might be redundant as the patient object holding them should already have mrn
        self.start_date = start_date #starting date of the ambulation
        self.start_time = start_time #starting time of the ambulation
        self.dur = duration
        self.dist = distance
        self.speed = speed
        self.amb_num = ambulation_number
        self.time_on_unit = -1 #Not sure what this is. Ask Dr. Searson for clarification again


    def print_amb_data(self):
        print("mrn:",self.mrn, "start_date:", self.start_date, "start_time:", self.start_time, "Ambulation num:", self.amb_num)
        print("Duration:", self.dur, "Distance:", self.dist, "Speed:", self.speed, )

class Day(object):

    # The class "constructor" - It's actually an initializer 
    def __init__(self, date, day_number):
        self.date = date #the date this Day represents 

        self.ambulations = [] # All the ambulations the patient made on this day
        self.num_ambulations = 0

        self.day_number = day_number #the day number this day is, i.e. 1st day they're in the unit, or 2nd, etc.

        self.max_dur = -1 #max ambulation duration
        self.mean_dur = -1
        self.min_dur = -1

        self.max_dist = -1 #max ambulation distance
        self.mean_dist = -1
        self.min_dist = -1

        self.max_speed = -1 #max ambulation speed
        self.mean_speed = -1
        self.min_speed = -1

    def add_ambulation(self, ambulation):
        self.ambulations.append(ambulation)

        self.mean_dist = self.add_to_mean(self.mean_dist, self.num_ambulations, ambulation.dist)
        self.mean_dur = self.add_to_mean(self.mean_dur, self.num_ambulations, ambulation.dur)
        self.mean_speed = self.add_to_mean(self.mean_speed, self.num_ambulations, ambulation.speed)

        self.max_dist = max(self.max_dist, ambulation.dist)
        self.max_dur = max(self.max_dur, ambulation.dur)
        self.max_speed = max(self.max_speed, ambulation.speed)

        self.min_dist = self.update_min(self.min_dist, ambulation.dist)
        self.min_dur = self.update_min(self.min_dur, ambulation.dur)
        self.min_speed = self.update_min(self.min_speed, ambulation.speed)

        self.num_ambulations += 1

    def add_to_mean(self, prev_mean, prev_size, value): # prev_mean and prev_size are the mean and size before this insertion
        if prev_size == 0: #this is the first ambulation being entered, so the mean is just the value
            return value
        else:
            return (prev_size * prev_mean + value) / (prev_size + 1) #lets us update a mean in O(1) time

    def update_min(self, curr_value, value): #curr_value is the current value of whatever we are passing in (i.e. min_dist, min_dur, min_speed)
        if self.num_ambulations == 0:
            return value
        else:
            return min(curr_value, value)

        




