import sys
import time
import stepperweblib

#   Direction in case one has to spin backwards
feed_direction = 1
take_direction = 1

#  Estimated size (inches)
feed_diameter = 47
take_diameter = 3

#  percentage over, in case (10%)
take_overage = 1.10
ticksperrev = 25000
pi = 3.1415926535897932384626433832795

feed_circumference = pi * feed_diameter
take_circumference = pi * take_diameter

#  Movement in inches linearly
MoveLength = 12

feed_ticks = MoveLength / feed_circumference * ticksperrev * feed_direction
take_ticks = MoveLength / take_circumference * ticksperrev * take_direction
print("feed ticks: {}   take ticks: {}".format(feed_ticks, take_ticks))

#  Calc a velocity based on radius? in inches per minute
LinearVelocity = 5
#  Make Velocity is 250 (about 5.6 on smaller side)
max_velocity = 250
feed_velocity = LinearVelocity / feed_circumference * ticksperrev / 60
take_velocity = LinearVelocity / take_circumference * ticksperrev / 60

if feed_velocity > max_velocity:
    feed_velocity = max_velocity
if take_velocity > max_velocity:
    take_velocity = max_velocity

print("feed velocity: {}   take velocity: {}".format(feed_velocity, take_velocity))

#  Create connects to motor controllers
feed = stepperweblib.StepperControl("10.0.1.70")
take = stepperweblib.StepperControl("10.0.1.71")


# feed states
# 0 = idle
# 1 = Button pressed, start move
# 2 = Moving (wait until done)
feed_state = 0

# take states
# 0 = idle
# 1 = halt (if tension)
# 2 = pull in (if slack)
take_state = 0

# communication flags
take_up = 0

count = 0
while True:
    # feed state machine
    if feed_state == 0:
        # doing nothing, waiting for button
        feed.MotorHalt()
        button = feed.CheckFlag()
        # button pressed, move to button state
        # Using momentary (logic reversed)
        take_up = 0
        if button == 0:
            feed_state = 1
    elif feed_state == 1:
        # check if button released
        button = feed.CheckFlag()
        if button == 1:
            feed_state = 2
            # move at the same time
            take_up = 1
            feed.MoveRelative(feed_velocity, feed_ticks)
    elif feed_state == 2:
        # moving check if done
        done = feed.CheckReached()
        # when done, stop motor, go to idle
        if done == 1:
            feed.MotorHalt()
            feed_state = 0

    if take_state == 0:
        # doing nothing, waiting for command from feed
        take.MotorHalt()

        # command move out of idle to slack
        if take_up == 1:
            take_state = 1
    elif take_state == 1:
        # waiting for slack
        take.MotorHalt()
        tension = take.CheckFlag()
        # if there is slack move
        if tension == 0:
            take_state = 2
            take.MoveRelative(take_velocity, take_ticks)
        # if there is slack, and feed motor isn't moving
        # then go back to idle (already halted)
        elif take_up == 0:
            take_state = 0

    elif take_state == 2:
        # When tension is made, stop
        tension = take.CheckFlag()
        # might happen multiple times
        if tension == 1:
            take.MotorHalt()
            take_state = 1

    count = count + 1
    print("count: {}   feed: {}   take: {}".format(count, feed_state, take_state))

    sys.stdout.flush()
    time.sleep(.1)
