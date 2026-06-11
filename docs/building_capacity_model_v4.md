# Building Capacity Model v4

This model replaces primary building-level “estimated residents” logic with residential capacity signals.

Rules:
- If PLUTO UnitsRes is present, residential_capacity_units = UnitsRes.
- If UnitsRes is missing but residential use is clear, capacity is estimated from ResArea or BldgArea using an average unit-size fallback.
- If land use / building class indicates non-residential, residential capacity, estimated household capacity, and under-5 capacity signal are 0.
- estimated_household_capacity equals residential capacity units; it is not observed occupancy.
- under5_capacity_signal = residential_capacity_units × local aggregate under-5 per household proxy.

Confidence:
- High: UnitsRes available and use clear.
- Medium: residential use clear but units estimated from ResArea/BldgArea.
- Low: weak inferred residential use.
- None: non-residential or no residential capacity detected.

Tooltip caveat: Under-5 capacity signal is modeled from residential unit capacity and aggregate census age patterns. It is not actual children living in this building. 5岁以下儿童潜力信号基于住宅单元承载能力和聚合人口年龄结构建模，不代表该建筑内真实儿童人数。
