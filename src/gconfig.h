/*
 * gconfig.h
 *
 *  Created on: Mar 16, 2016
 *  Author: sdagar
 */

#ifndef GCONFIG_H_
#define GCONFIG_H_
#define FINE 100
#define SPEED_R 12
#define SPEED_N 6
#define SPEED_DIF_X 0.2
#define SPEED_DIF_Y 0.2
#define SCALE 1
#define SX 1.176
#define SY 1
#define KX 5
#define KY 5
#define NX (SPEED_R*(KX+1)/(2*SPEED_DIF_X))+1
#define NY (SPEED_R*(KY+1)/(2*SPEED_DIF_Y))+1
#define FL (int)(NX>NY?NX:NY)
#define MAXT 5
#define ALGO 0
#endif /* GCONFIG_H_ */
