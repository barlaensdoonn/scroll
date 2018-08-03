import sys
import time
import stepperweblib

# Direction in case one has to spin backwards
feed_direction = -1
take_direction = 1

# run for ever
always_run = 1

# Estimated size (inches)
feed_diameter = 47
take_diameter = 3
# percentage over
take_overage = 1.25
ticksperrev = 25000
pi = 3.1415926535897932384626433832795

feed_circumference = pi * feed_diameter
take_circumference = pi * take_diameter

# Movement in inches linearly
MoveLength = 12
# How much to move per tick/tock
MoveSteps = 4
# only move distance of tick/tock
# will be recalculated as needed
feed_ticks = MoveLength / feed_circumference * ticksperrev * feed_direction
take_ticks = MoveLength / take_circumference * ticksperrev * take_direction * take_overage

print "Ticks: ", feed_ticks, take_ticks

# Calc a velocity based on radius?
# in inches per minute
LinearVelocity = .5
# Make Velocity is 250 (about 5.6 on smaller side)
max_velocity = 250
feed_velocity = LinearVelocity / feed_circumference * ticksperrev / 60
take_velocity = LinearVelocity / take_circumference * ticksperrev / 60

# in case
if(feed_velocity > max_velocity):
    feed_velocity = max_velocity
if(take_velocity > max_velocity):
    take_velocity = max_velocity

print "Velocity: ", feed_velocity, take_velocity

# Create connects to motor controllers
feed = stepperweblib.StepperControl("10.0.1.70")
take = stepperweblib.StepperControl("10.0.1.71")

# single state machine
# 0 = idle
# 1 = Button pressed, start move (partial)
# 2 = Moving (wait until done)
# 3 = Move in Slack (stop when done, back to move
state = 0

feed.motor_halt()
take.motor_halt()


MoveLeft = 0
count = 0
while True:

    # state machine
    if(state == 0):
        # doing nothing, waiting for button
        # feed.motor_halt()
        # take.motor_halt()

        button = feed.check_flag()
        # button pressed, move to button state
        # Using momentary (logic reversed)
        if(button == 0 or always_run):
            state = 1
            # Store the total movement
            MoveLeft = MoveLength
    elif(state == 1):
        # check if button released
        button = feed.check_flag()
        if(button == 1):
            state = 2
            CurrLength = 0
            # Will moves in ticks
            if(MoveLeft > MoveSteps):
                CurrLength = MoveSteps
                MoveLeft -= MoveSteps
            else:
                CurrLength = MoveLeft
                MoveLeft = 0
            # Calculate ticks base on tick of whats left of a tick
            feed_ticks = CurrLength / feed_circumference * ticksperrev * feed_direction
            take_ticks = CurrLength / take_circumference * ticksperrev * take_direction * take_overage
            # Do Actual movement
            feed.move_relative(feed_velocity, feed_ticks)
    elif(state == 2):
        # moving check if done
        done = feed.check_reached()
        # when done, stop motor
        # start taking in slack
        if(done == 1):
            feed.motor_halt()
            state = 3
            # Move in either ticks or what is left (has some overage)
            take.move_relative(take_velocity, take_ticks)
    elif(state == 3):
        # check to see if tensioned

        # When tension is made, stop
        tension = take.check_flag()
        # backup, full motion
        bdone = take.check_reached()

        # Happens once per tick/tock
        if(tension == 1 or bdone == 1):
            take.motor_halt()
            # if there is more ticks, do another
            if(MoveLeft > 0):
                state = 1
            # if there are no more, go to idle
            else:
                state = 0

    count += 1
    print "Count: ", count, " State: ", state,  " Left: ", MoveLeft

    sys.stdout.flush()
    time.sleep(.1)
