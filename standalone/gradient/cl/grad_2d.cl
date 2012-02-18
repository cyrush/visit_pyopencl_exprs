//
// grad_2d.cl
// rectilinear gradient (2-nd order)
//

__kernel void exe(__global const int   *d,
                  __global const float *x,
                  __global const float *y,
                  __global const float *v, 
                  __global float *o)
{
  int gid = get_global_id(0);
  int di = d[0]-1;
  int dj = d[1]-1;

  int zi = gid % di;
  int zj = gid / di;
  
  // for rectilinear, we only need 2 points to get dx,dy
  int pi0 = zi + zj*(di+1);
  int pi1 = zi + 1 + (zj+1)*(di+1);
  
  float vv = v[gid];

  float vx0 = vv;
  float vx1 = vv;
  if(zi > 0)    vx0 = v[gid-1];
  if(zi < di-1) vx1 = v[gid+1];

  float vy0 = vv;
  float vy1 = vv;
  if(zj > 0)    vy0 = v[zi + (zj-1)*di];
  if(zj < dj-1) vy1 = v[zi + (zj+1)*di];

  float x0 = x[pi0];
  float x1 = x[pi1];

  float y0 = y[pi0];
  float y1 = y[pi1];

  float dx = (x1 - x0);
  float dy = (y1 - y0);
  float dvdx = .5  * (vx1 - vx0) / dx;
  float dvdy = .5  * (vy1 - vy0) / dy;

  // forward diff @ boundries
  if(zi == 0)    dvdx = (vx1 - vx0)/dx;
  if(zi == di-1) dvdx = (vx1 - vx0)/dx;
  if(zj == 0)    dvdy = (vy1 - vy0)/dy;
  if(zj == dj-1) dvdy = (vy1 - vy0)/dy;

  o[gid*3]   = dvdx;
  o[gid*3+1] = dvdy;
}