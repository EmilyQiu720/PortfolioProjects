/*----------------------------------------------------------------------------*/
/* Copyright (c) 2017-2018 FIRST. All Rights Reserved.                        */
/* Open Source Software - may be modified and shared by FRC teams. The code   */
/* must be accompanied by the FIRST BSD license file in the root directory of */
/* the project.                                                               */
/*----------------------------------------------------------------------------*/

package org.usfirst.frc.team7146.robot.subsystems;

import org.usfirst.frc.team7146.robot.RobotMap;
import org.usfirst.frc.team7146.robot.commands.TeleopTankDriveCommand;
import edu.wpi.first.wpilibj.Joystick;
import edu.wpi.first.wpilibj.Spark;
import edu.wpi.first.wpilibj.command.Subsystem;
import edu.wpi.first.wpilibj.drive.DifferentialDrive;

/**
 * An example subsystem.  You can replace me with your own Subsystem.
 */
public class DriveTrainSubsystem extends Subsystem {
	// Put methods for controlling this subsystem
	// here. Call these from Commands.
	Spark mLeftMotor = new Spark(RobotMap.leftMtorNumber);
	Spark mRightMotor = new Spark(RobotMap.rightMotorNumber);
	DifferentialDrive mDifferentialDrive = new DifferentialDrive(mLeftMotor, mRightMotor);

	public void initDefaultCommand() {
		// Set the default command for a subsystem here.
		setDefaultCommand(new TeleopTankDriveCommand());
	}
	
	public void mDriveTank(Joystick mJoystick) {
		mDifferentialDrive.tankDrive(mJoystick.getY()*RobotMap.TankDriveleftSpeed, 
				mJoystick.getThrottle()*RobotMap.TankDriverightSpeed);
	}
	
	public void stopDrive() {
		mLeftMotor.stopMotor();
		mRightMotor.stopMotor();
	}
}
