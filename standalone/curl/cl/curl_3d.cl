//
// curl_3d.cl
//

__kernel void exe(__global const float *dfx,
                  __global const float *dfy,
                  __global const float *dfz,
                  __global float *o)
{
  int gid = get_global_id(0);

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