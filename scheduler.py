import sched, time
s = sched.scheduler(time.time, time.sleep)

def print_time(): 
	print "From print_time",time.time()

def print_some_times():
	print("in print_some_times 0")
	s.enter(5, 1, print_time, ())
	print("in print_some_times 1")
	s.enter(10, 1, print_time, ())
	print("in print_some_times 2")
	s.run()
	print time.time()

print_some_times()
