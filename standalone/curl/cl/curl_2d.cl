//
// curl_2d.cl
// curl when dz is 0
//

__kernel void exe(__global const float *dfx,
                  __global const float *dfy,
                  __global float *o)
{
  int gid = get_global_id(0);
  float dfxdy = dfx[gid*3+2];
  float dfydx = dfy[gid*3];
  o[gid] = dfydx - dfxdy;
}