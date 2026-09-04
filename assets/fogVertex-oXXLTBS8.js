import{bG as o}from"./Queen-DyeT_Shs.js";const e="fogVertex",r=`#ifdef FOG
vFogDistance=(view*worldPos).xyz;
#endif
`;o.IncludesShadersStore[e]||(o.IncludesShadersStore[e]=r);const t={name:e,shader:r};export{t as f};
