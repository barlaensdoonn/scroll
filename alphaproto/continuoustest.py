#!/usr/bin/python3
# authored by Gary Stein at AlphaProto June 2018
# refactored for python 3 by Brandon Aleson July 2018
# updated 7/6/18

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
move_length = 12

feed_ticks = move_length / feed_circumference * ticksperrev * feed_direction
take_ticks = move_length / take_circumference * ticksperrev * take_direction
print("feed ticks: {}   take ticks: {}".format(feed_ticks, take_ticks))

#  Calc a velocity based on radius? in inches per minute
linear_velocity = 5
#  Make Velocity is 250 (about 5.6 on smaller side)
max_velocity = 250
feed_velocity = linear_velocity / feed_circumference * ticksperrev / 60
take_velocity = linear_velocity / take_circumference * ticksperrev / 60

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
        feed.motor_halt()
        button = feed.check_flag()
        # button pressed, move to button state
        # Using momentary (logic reversed)
        take_up = 0
        if button == 0:
            feed_state = 1
    elif feed_state == 1:
        # check if button released
        button = feed.check_flag()
        if button == 1:
            feed_state = 2
            # move at the same time
            take_up = 1
            feed.move_relative(feed_velocity, feed_ticks)
    elif feed_state == 2:
        # moving check if done
        done = feed.check_reached()
        # when done, stop motor, go to idle
        if done == 1:
            feed.motor_halt()
            feed_state = 0

    if take_state == 0:
        # doing nothing, waiting for command from feed
        take.motor_halt()

        # command move out of idle to slack
        if take_up == 1:
            take_state = 1
    elif take_state == 1:
        # waiting for slack
        take.motor_halt()
        tension = take.check_flag()
        # if there is slack move
        if tension == 0:
            take_state = 2
            take.move_relative(take_velocity, take_ticks)
        # if there is slack, and feed motor isn't moving
        # then go back to idle (already halted)
        elif take_up == 0:
            take_state = 0

    elif take_state == 2:
        # When tension is made, stop
        tension = take.check_flag()
        # might happen multiple times
        if tension == 1:
            take.motor_halt()
            take_state = 1

    count = count + 1
    print("count: {}   feed: {}   take: {}".format(count, feed_state, take_state))

    sys.stdout.flush()
    time.sleep(.1)
