#!/usr/bin/env python3
from tf_transformations import euler_from_quaternion
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

import time
from math import *


class TurtleController(Node):
    currentPose = []
    targets = []
    currentTarget = 0
    angleSet = False
    
    def __init__(self):
        super().__init__('turtle_controller')
        self.publisher_ = self.create_publisher(
            msg_type=Twist, 
            topic='cmd_vel',
            qos_profile=10
        )
        self.pose_subscription = self.create_subscription(
            msg_type=Odometry,
            topic='/odom',
            callback=self.pose_callback,
            qos_profile=10
        )
        self.timer_ = self.create_timer(0.1, self.move_turtle)
        self.twist_msg_ = Twist()
        

    def move_turtle(self):
        if self.currentTarget >= len(self.targets):
            self.twist_msg_.linear.x = 0.0
            self.twist_msg_.angular.z = 0.0
            self.publisher_.publish(self.twist_msg_)
            return
        
        nextPose = self.targets[self.currentTarget]
        
        dx = nextPose[0] - self.currentPose[0]
        dy = nextPose[1] - self.currentPose[1]
        dist = sqrt(dx*dx + dy*dy)
        ang = atan2(dy, dx) - self.currentPose[2]
        direction = ang / abs(ang)
        
        if not self.angleSet:
            if abs(ang) > 0.01:
                self.twist_msg_.linear.x = 0.0
                self.twist_msg_.angular.z = 0.1 * direction
            else:
                self.twist_msg_.angular.z = 0.0
                self.angleSet = True

        if self.angleSet:
            if dist > 0.1:
                self.twist_msg_.linear.x = 0.1
            else:
                self.twist_msg_.linear.x = 0.0
                self.currentTarget += 1
                self.angleSet = False
        
        self.publisher_.publish(self.twist_msg_)
    
    def pose_callback(self, msg):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        z = msg.pose.pose.position.z
        ang = msg.pose.pose.orientation
        _, _, theta = euler_from_quaternion([ang.x, ang.y, ang.z, ang.w])
        self.get_logger().info(f"x={x}, y={y}, theta={theta}")
        self.currentPose = [x, y, theta]
        
        


def main(args=None):
    rclpy.init()
    turtle_controller = TurtleController()
    
    # Define the targets for the robot to follow
    turtle_controller.targets = [
        [2, 1],
        [4, 3],
        [0, 0],
    ]
    
    rclpy.spin(turtle_controller)
    turtle_controller.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()