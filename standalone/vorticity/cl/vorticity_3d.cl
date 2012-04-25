//
// vorticity_3d.cl
//

__kernel void vorticity_3d(int *d, float *x, float *y, float *z, float *v, float *o)
{
  int gid = get_global+id(0);
  
  float ox[sizeof(x)/sizeof(float)];
  float oy[sizeof(y)/sizeof(float)];
  float oz[sizeof(z)/sizeof(float)];
    
  grad_3d(gid, x, x, y, z, v, ox);
  grad_3d(gid, y, x, y, z, v, oy);
  grad_3d(gid, z, x, y, z, v, oz);
  curl_3d(gid, ox, oy, oz, o);

}


void curl_3d(int gid, float *dfx, float *dfy, float *dfz, float *o)
{
  float dfzdy = dfz[gid*3+1];
  float dfydz = dfy[gid*3+2];

  float dfxdz = dfx[gid*3+2];
  float dfzdx = dfz[gid*3];

  float dfydx = dfy[gid*3];
  float dfxdy = dfx[gid*3+1];

  o[gid*3]   = dfzdy - dfydz;
  o[gid*3+1] = dfxdz - dfzdx;  
  o[gid*3+2] = dfydx - dfxdy;
}


void grad_3d(int gid, int *d, float *x, float *y, float *z, float *v, float *o)
{
  int gid = get_global_id(0);
  int di = d[0]-1;
  int dj = d[1]-1;
  int dk = d[2]-1;

  int zi = gid % di;
  int zj = (gid / di) % dj;
  int zk =  (gid / di) / dj;

  // for rectilinear, we only need 2 points to get dx,dy,dz
  int pi0 = zi + zj*(di+1) + zk*(di+1)*(dj+1);
  int pi1 = zi + 1 + (zj+1)*(di+1) + (zk+1)*(di+1)*(dj+1);
  
  float vv = v[gid];

  float vx0 = vv;
  float vx1 = vv;
  if(zi > 0)    vx0 = v[gid-1];
  if(zi < di-1) vx1 = v[gid+1];

  float vy0 = vv;
  float vy1 = vv;
  if(zj > 0)    vy0 = v[zi + (zj-1)*di + zk*(di*dj)];
  if(zj < dj-1) vy1 = v[zi + (zj+1)*di + zk*(di*dj)];

  float vz0 = vv;
  float vz1 = vv;
  if(zk > 0)    vz0 = v[zi + zj*di + (zk-1)*(di*dj)];
  if(zk < dk-1) vz1 = v[zi + zj*di + (zk+1)*(di*dj)];


  float x0 = x[pi0];
  float x1 = x[pi1];

  float y0 = y[pi0];
  float y1 = y[pi1];

  float z0 = z[pi0];
  float z1 = z[pi1];


  float dx = (x1 - x0);
  float dy = (y1 - y0);
  float dz = (z1 - z0);
  float dvdx = .5  * (vx1 - vx0) / dx;
  float dvdy = .5  * (vy1 - vy0) / dy;
  float dvdz = .5  * (vz1 - vz0) / dz;

  // forward diff @ boundries
  if(zi == 0)    dvdx = (vx1 - vx0)/dx;
  if(zi == di-1) dvdx = (vx1 - vx0)/dx;
  if(zj == 0)    dvdy = (vy1 - vy0)/dy;
  if(zj == dj-1) dvdy = (vy1 - vy0)/dy;
  if(zk == 0)    dvdz = (vz1 - vz0)/dz;
  if(zk == dk-1) dvdz = (vz1 - vz0)/dz;


  o[gid*3]   = dvdx;
  o[gid*3+1] = dvdy;
  o[gid*3+2] = dvdz;
}