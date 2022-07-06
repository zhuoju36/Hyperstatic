## 更新日志
2022-07-06 v0.1.15
增加后处理内核接口:
- 梁单元变形解析 core.api.result_get_beam_deformation

2022-07-05 v0.1.14 
- 修复错误
- 增加用于推导单元的core.fe_model.meta模块

2022-07-04 v0.1.13 
调整内核接口
- 集成数据从solver解耦 core.api.assemble
- 位移解析方法参数列表调整

增加后处理内核接口
- 结构自振周期解析 core.api.result_get_structural_period
- 结构自振模态解析 core.api.result_get_structural_vibration_mode
- 结构反力解析 core.api.result_get_structural_reaction
- 结点位移解析 core.api.result_get_nodal_displacement
- 结点反力解析 core.api.result_get_nodal_reaction
- 梁端力解析 core.api.result_get_beam_end_force

2022-06-21 v0.1.12 
增加求解器内核接口
- 增加特征值模态求解 core.api.solve_modal

2022-05-29 v0.1.10 
- 增加梁集中荷载设置 core.api.set_beam_load_concentrated
- 增加梁局部荷载设置 core.api.set_beam_load_distributed
