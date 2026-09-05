import{bW as s}from"./Queen-BBI2u1hW.js";const e="fogVertex",o=`#ifdef FOG
#ifdef SCENE_UBO
vertexOutputs.vFogDistance=(scene.view*worldPos).xyz;
#else
vertexOutputs.vFogDistance=(uniforms.view*worldPos).xyz;
#endif
#endif
`;s.IncludesShadersStoreWGSL[e]||(s.IncludesShadersStoreWGSL[e]=o);const r={name:e,shader:o};export{r as f};
