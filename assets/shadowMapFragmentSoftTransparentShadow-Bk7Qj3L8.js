import{S as o}from"./QueenCombBabylon-DOdGX8_Q.js";import"./react-Be6y7_DR.js";import"./three-C7rSOEFP.js";import"./Queen-DB_P-JXd.js";import"./index--wm36luZ.js";import"./motion-CsGAkEsf.js";import"./router-BHJoP3Ih.js";const r="shadowMapFragmentSoftTransparentShadow",a=`#if SM_SOFTTRANSPARENTSHADOW==1
if ((bayerDither8(floor(((fragmentInputs.position.xy)%(8.0)))))/64.0>=uniforms.softTransparentShadowSM.x*alpha) {discard;}
#endif
`;o.IncludesShadersStoreWGSL[r]||(o.IncludesShadersStoreWGSL[r]=a);const d={name:r,shader:a};export{d as shadowMapFragmentSoftTransparentShadowWGSL};
