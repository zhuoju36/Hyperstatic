## 更新日志
2022-07-15 v0.2.0
调整内核层类型
- 增加Material类型
- 增加BeamSection类型
- 调整Beam类为SimpleBeam类，原Beam类依赖于BeamSection类型
- 调整core.Api.set_nodal_restraints为全局约束设置，工况约束改为 core.Api.set_loadcase_nodal_restraints，前者为首选项，若设置后者，则前者集成时被自动覆盖。
增加前处理内核接口
- 各向同性材料 core.Api.add_isotropic_material
- 一般梁截面 core.Api.add_beam_section_general 
- 工字形截面 core.Api.add_beam_section_I
- 箱型截面 core.Api.add_beam_section_box
- 矩形截面 core.Api.add_beam_section_rectangle
- 圆形截面 core.Api.add_beam_section_circle
- 圆管截面 core.Api.add_beam_section_pipe
调整内核层可视化接口
- 基本模型视图 app.viz.viz_core.model_basic.BasicViewer
- 荷载视图 app.viz.viz_core.model_load.LoadViewer
- 分析结果视图 app.viz.viz_core.result_deformation.ResultViewer
性能优化

2022-07-06 v0.1.15
增加后处理内核接口:
- 梁单元变形解析 core.Api.result_get_beam_deformation
增加应用
- 内核层可视化 app.viz.viz_core

2022-07-05 v0.1.14 
- 修复错误
- 增加用于推导单元的core.fe_model.meta模块

2022-07-04 v0.1.13 
调整内核接口
- 集成数据从solver解耦 core.Api.assemble
- 位移解析方法参数列表调整

增加后处理内核接口
- 结构自振周期解析 core.Api.result_get_structural_period
- 结构自振模态解析 core.Api.result_get_structural_vibration_mode
- 结构反力解析 core.Api.result_get_structural_reaction
- 结点位移解析 core.Api.result_get_nodal_displacement
- 结点反力解析 core.Api.result_get_nodal_reaction
- 梁端力解析 core.Api.result_get_beam_end_force

2022-06-21 v0.1.12 
增加求解器内核接口
- 增加特征值模态求解 core.Api.solve_modal

2022-05-29 v0.1.10 
- 增加梁集中荷载设置 core.Api.set_beam_load_concentrated
- 增加梁局部荷载设置 core.Api.set_beam_load_distributed
