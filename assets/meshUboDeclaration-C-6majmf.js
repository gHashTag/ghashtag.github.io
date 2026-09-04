import{bG as s}from"./Queen-DyeT_Shs.js";const e="meshUboDeclaration",r=`struct Mesh {world : mat4x4<f32>,
visibility : f32,};var<uniform> mesh : Mesh;
#define WORLD_UBO
`;s.IncludesShadersStoreWGSL[e]||(s.IncludesShadersStoreWGSL[e]=r);const t={name:e,shader:r};export{t as m};
