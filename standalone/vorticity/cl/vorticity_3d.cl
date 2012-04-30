//
// vorticity_3d.cl
//

__kernel void  vorticity_3d(__global const int   *d,
                         __global const float *x,
                         __global const float *y,
                         __global const float *z,
                         __global const float *u, 
                         __global const float *v, 
                         __global const float *w,
                         __global float *o)
{
     int gid = get_global_id(0);
     int di = d[0]-1;
     int dj = d[1]-1;
     int dk = d[2]-1;

     int zi = gid % di;
     int zj = (gid / di) % dj;
     int zk = (gid / di) / dj;

     // for rectilinear, we only need 2 points to get dx,dy,dz
     int pi0 = zi + zj*(di+1) + zk*(di+1)*(dj+1);
     int pi1 = zi + 1 + (zj+1)*(di+1) + (zk+1)*(di+1)*(dj+1);
     
     // x component
     float uv = u[gid];
   
     float ux0 = uv;
     float ux1 = uv;
     if(zi > 0)      ux0 = u[gid-1];
     if(zi < (di-1)) ux1 = u[gid+1];
   
     float uy0 = uv;
     float uy1 = uv;
     if(zj > 0)      uy0 = u[gid - di];
     if(zj < (dj-1)) uy1 = u[gid + di];
   
     float uz0 = uv;
     float uz1 = uv;
     if(zk > 0)      uz0 = u[gid - (di*dj)];
     if(zk < (dk-1)) uz1 = u[gid + (di*dj)];
   
     // y component  
     float vv = v[gid];
   
     float vx0 = vv;
     float vx1 = vv;
     if(zi > 0)    vx0 = v[gid-1];
     if(zi < (di-1)) vx1 = v[gid+1];
   
     float vy0 = vv;
     float vy1 = vv;
     if(zj > 0)      vy0 = v[gid - di];
     if(zj < (dj-1)) vy1 = v[gid + di];
   
     float vz0 = vv;
     float vz1 = vv;
     if(zk > 0)      vz0 = v[gid - (di*dj)];
     if(zk < (dk-1)) vz1 = v[gid + (di*dj)];
   
     // z component
     float wv = w[gid];
   
     float wx0 = wv;
     float wx1 = wv;
     if(zi > 0)      wx0 = w[gid-1];
     if(zi < (di-1)) wx1 = w[gid+1];
   
     float wy0 = wv;
     float wy1 = wv;
     if(zj > 0)      wy0 = w[gid - di];
     if(zj < (dj-1)) wy1 = w[gid + di];
   
     float wz0 = wv;
     float wz1 = wv;
     if(zk > 0)      wz0 = w[gid - (di*dj)];
     if(zk < (dk-1)) wz1 = w[gid + (di*dj)];
   
     float x0 = x[pi0];
     float x1 = x[pi1];
   
     float y0 = y[pi0];
     float y1 = y[pi1];
   
     float z0 = z[pi0];
     float z1 = z[pi1];
   
     float dx = (x1 - x0);
     float dy = (y1 - y0);
     float dz = (z1 - z0);
   
     float dudy = (uy1 - uy0) / dy;
     float dudz = (uz1 - uz0) / dz;
     
     float dvdx = (vx1 - vx0) / dx;
     float dvdz = (vz1 - vz0) / dz;
     
     float dwdx = (wx1 - wx0) / dx;
     float dwdy = (wy1 - wy0) / dy;
   
    //forward diff @ boundries
    if( (zi != 0) && (zi != (di-1)))
    {
       dvdx *= .5;
       dwdx *= .5;
    }

    if( (zj != 0) && (zj != (dj-1)))
    {
       dudy *= .5;
       dwdy *= .5;
    }

    if( (zk != 0) && (zk != (dk-1)))
    {    
       dudz *= .5;
       dvdz *= .5;
    }

    o[gid*3]   = dwdy - dvdz;
    o[gid*3+1] = dudz - dwdx;  
    o[gid*3+2] = dvdx - dudy;
}
