# C5.51 Fulfillment / Effective Output Audit

## 결론 요약

C5.51의 `demand_fulfillment_rate`는 **load count 기준**이다. raw tonnage 기준도 아니고, `effective_output` 또는 grade-adjusted output 기준도 아니다.

따라서 H1/H2가 낮은 grade route, 예를 들어 R_C1/R_C2를 많이 선택해도 지정된 load 수를 모두 완료하면 fulfillment는 `1.000`이 된다. 낮은 grade 선택은 `effective_output` KPI에는 반영되지만, 현재 C5.51의 TCO/reward에는 직접 반영되지 않는다.

## 확인 항목별 결과

| 항목 | 판정 | 근거 |
|---|---|---|
| 1. fulfillment가 load count 기준인지 | Yes | `fulfillment = completed_loads / total_demand` |
| 2. fulfillment가 raw tonnage 기준인지 | No | `payload_ton`은 fulfillment 계산에 사용되지 않음 |
| 3. fulfillment가 effective_output 또는 grade-adjusted output 기준인지 | No | `effective_output`은 별도 KPI로 저장될 뿐 fulfillment 분모/분자에 없음 |
| 4. target demand 단위 | loads/day | `configs/c5_51.yaml`의 `demand.daily_demand_loads: 210` |
| 5. effective_output이 TCO/reward에 직접 반영되는지 | No | `total_tco = pm + cm + downtime + degradation + unmet` |
| 6. 낮은 grade route 선택 후에도 fulfillment 1.000 가능 여부 | Yes | 성공한 haul/load 수만 충족하면 grade와 무관하게 fulfillment 1.000 |

## 코드 근거

### Demand Target 단위

C5.51 config의 demand target은 tonnage나 grade-adjusted output이 아니라 load count다.

```yaml
demand:
  daily_demand_loads: 210
  operating_hours_per_day: 24
  default_grade: 0.008
  ore_ton_per_load: 350
```

`mine_env/simulator_c5_51.py`에서는 이 값을 그대로 일일 load quota로 읽는다.

```python
daily_demand = int(config["demand"]["daily_demand_loads"])
per_step_cap = max(int(math.ceil(daily_demand / steps_per_day)), 1)
```

매일 `total_demand`도 load 단위로 누적된다.

```python
demand_remaining = daily_demand
counts["total_demand"] += daily_demand
```

### Completed Load Count

C5.51에서 route 실행이 성공하면 demand가 1 감소하고, completed load가 1 증가한다.

```python
demand_remaining -= 1
completed_today += 1
counts["completed_loads"] += 1
```

이때 route의 grade나 payload는 `completed_loads` 증가 여부에 영향을 주지 않는다. 실패 없이 route가 완료되면 한 load로 계산된다.

### Fulfillment 계산

최종 fulfillment는 load count 비율이다.

```python
fulfillment = counts["completed_loads"] / counts["total_demand"] if counts["total_demand"] else 1.0
```

summary에는 다음과 같이 저장된다.

```python
"completed_loads": counts["completed_loads"],
"unmet_demand": counts["unmet_loads"],
"demand_fulfillment_rate": round(fulfillment, 6),
```

즉 `demand_fulfillment_rate`의 분자는 완료 load 수, 분모는 목표 load 수다.

## Effective Output 처리

C5.51은 grade-adjusted output을 별도 KPI로 계산한다.

```python
effective_output += float(config["mine"]["payload_ton"]) * float(route["grade_index"])
```

예를 들어:

- R_A route: `350 * 0.90 = 315 effective units/load`
- R_B route: `350 * 0.80 = 280 effective units/load`
- R_C route: `350 * 0.70 = 245 effective units/load`

하지만 이 값은 summary의 `effective_output`에만 들어간다.

```python
"effective_output": round(effective_output, 3),
```

`effective_output`은 fulfillment 계산에도, TCO 계산에도 직접 들어가지 않는다.

## TCO / Reward 반영 여부

C5.51의 total TCO는 다음 합계다.

```python
total_tco = sum(totals.values())
```

`totals`는 다음 비용만 포함한다.

```python
totals = {"pm": 0.0, "cm": 0.0, "downtime": 0.0, "degradation": 0.0, "unmet": 0.0}
```

그리고 summary에는 다음 cost split으로 저장된다.

```python
"pm_cost": round(totals["pm"], 6),
"cm_cost": round(totals["cm"], 6),
"downtime_cost": round(totals["downtime"], 6),
"degradation_cost": round(totals["degradation"], 6),
"unmet_demand_cost": round(totals["unmet"], 6),
```

Unmet demand cost도 unmet load count 기준이다.

```python
totals["unmet"] += cost_model.unmet_demand_cost(unmet)
```

`mine_env/costs_c5_3.py`의 cost model도 unmet load 수에 penalty를 곱한다.

```python
def unmet_demand_cost(self, unmet_loads: float) -> float:
    return float(unmet_loads) * self.unmet_penalty
```

따라서 low-grade route를 선택해서 effective output이 낮아져도, load count quota만 채우면 unmet penalty는 발생하지 않는다.

## H1/H2 Fulfillment 1.000의 의미

C5.51 smoke 결과에서 H1/H2가 fulfillment `1.000`을 달성한 것은 다음 의미다.

- H1/H2가 목표 load 수를 모두 완료했다.
- H1/H2가 목표 raw tonnage를 모두 완료했다는 의미는 아니다. 다만 payload가 route별로 고정 350으로 가정되므로 load count가 같으면 raw tonnage도 암묵적으로 같다고 볼 수 있다.
- H1/H2가 목표 grade-adjusted output을 모두 완료했다는 의미는 아니다.
- H1/H2가 낮은 grade route를 많이 선택하면 `effective_output`은 H3/H4보다 낮을 수 있다.

실제로 C5.51 smoke report에서는 H1/H2가 full fulfillment를 달성하면서도 effective output이 H3/H4보다 낮았다.

| Policy | Fulfillment | Effective Output 경향 |
|---|---:|---|
| H1 | 1.000 | 낮은 grade route 비중 때문에 H3/H4보다 낮음 |
| H2 | 1.000 | 낮은 grade route 비중 때문에 H3/H4보다 낮음 |
| H3 | 1.000 | value route 선택으로 H1/H2보다 높음 |
| H4 | 1.000 | route 분산으로 H1/H2보다 높음 |

## C5.4 / C5.5 / C5.51 비교

| Version | Fulfillment 기준 | Grade/output의 목적함수 반영 | 비고 |
|---|---|---|---|
| C5.4 | completed loads / total demand loads | 직접 반영 없음 | route grade는 policy scoring에 쓰일 수 있지만 TCO에는 직접 수익으로 들어가지 않음 |
| C5.5 | completed loads / total demand loads | 직접 반영 없음 | `effective_output = payload * shovel.grade_index`는 KPI |
| C5.51 | completed loads / total demand loads | 직접 반영 없음 | `effective_output = payload * route.grade_index`는 KPI |

## 해석상 주의점

C5.51에서 H1/H2의 fulfillment 개선은 "생산량 기준 output을 모두 만족했다"는 뜻이 아니라, "요구 load count를 모두 만족했다"는 뜻이다.

현재 구조에서는 다음이 동시에 가능하다.

1. H1/H2가 R_C1/R_C2 같은 낮은 grade route를 많이 선택한다.
2. 모든 daily load quota를 채운다.
3. fulfillment는 `1.000`이 된다.
4. effective output은 high-grade route를 더 많이 선택한 정책보다 낮다.
5. TCO는 effective output 손실을 직접 벌점으로 보지 않는다.

따라서 C5.51의 smoke ranking을 해석할 때는 `demand_fulfillment_rate`와 `effective_output`을 함께 봐야 한다. 특히 H1/H2가 low-risk, low-grade route 중심으로 full load quota를 만족한 경우, TCO 관점에서는 좋아 보일 수 있지만 grade-adjusted production 관점에서는 H3/H4보다 낮은 성과일 수 있다.

## 진단 결론

C5.51의 current implementation은 load-count fulfillment model이다. 이는 C5.4/C5.5의 normalized TCO framing과 일관되지만, C5.51의 facility-route 실험에서 grade-adjusted production trade-off를 해석하려면 `effective_output`을 별도 핵심 KPI로 반드시 병렬 보고해야 한다.

코드 수정 없이 진단만 수행한 결과, H1/H2의 fulfillment `1.000`은 낮은 grade route 선택과 모순되지 않는다. 현재 모델에서는 "몇 load를 완료했는가"가 fulfillment를 결정하고, "그 load가 얼마만큼의 grade-adjusted output을 만들었는가"는 별도 KPI로만 남는다.
