from typing import List, Optional
from sqlalchemy import desc
from server.db.models.audit_rule_model import AuditRuleModel
from server.db.session import with_session


@with_session
def add_audit_rule(
    session,
    name: str,
    description: str = "",
    chapter_keywords: list = None,
    judge_logic: str = "",
) -> int:
    """
    新增审计规则，返回自增ID
    """
    if chapter_keywords is None:
        chapter_keywords = []
    m = AuditRuleModel(
        name=name,
        description=description,
        chapter_keywords=chapter_keywords,
        judge_logic=judge_logic,
    )
    session.add(m)
    session.commit()
    return m.id


@with_session
def get_audit_rule_by_id(session, rule_id: int) -> Optional[dict]:
    """
    根据ID获取审计规则，返回字典（避免session关闭后访问属性报错）
    """
    r = session.query(AuditRuleModel).filter_by(id=rule_id).first()
    if r is None:
        return None
    return {
        "id": r.id,
        "name": r.name,
        "description": r.description,
        "chapter_keywords": r.chapter_keywords,
        "judge_logic": r.judge_logic,
        "create_time": r.create_time.strftime("%Y-%m-%d %H:%M:%S") if r.create_time else None,
        "update_time": r.update_time.strftime("%Y-%m-%d %H:%M:%S") if r.update_time else None,
    }


@with_session
def list_audit_rules(
    session,
    limit: int = 100,
    offset: int = 0,
) -> List[dict]:
    """
    获取审计规则列表，按时间倒序
    """
    rules = (
        session.query(AuditRuleModel)
        .order_by(desc(AuditRuleModel.update_time))
        .offset(offset)
        .limit(limit)
        .all()
    )
    data = []
    for r in rules:
        data.append({
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "chapter_keywords": r.chapter_keywords,
            "judge_logic": r.judge_logic,
            "create_time": r.create_time.strftime("%Y-%m-%d %H:%M:%S") if r.create_time else None,
            "update_time": r.update_time.strftime("%Y-%m-%d %H:%M:%S") if r.update_time else None,
        })
    return data


@with_session
def update_audit_rule(
    session,
    rule_id: int,
    name: str = None,
    description: str = None,
    chapter_keywords: list = None,
    judge_logic: str = None,
) -> bool:
    """
    更新审计规则（只更新传入的非None字段）
    """
    m = session.query(AuditRuleModel).filter_by(id=rule_id).first()
    if m is None:
        return False
    if name is not None:
        m.name = name
    if description is not None:
        m.description = description
    if chapter_keywords is not None:
        m.chapter_keywords = chapter_keywords
    if judge_logic is not None:
        m.judge_logic = judge_logic
    session.add(m)
    session.commit()
    return True


@with_session
def delete_audit_rule(session, rule_id: int) -> bool:
    """
    删除审计规则
    """
    result = session.query(AuditRuleModel).filter_by(id=rule_id).delete()
    session.commit()
    return result > 0


@with_session
def audit_rule_exists(session, rule_id: int) -> bool:
    """
    检查审计规则是否存在
    """
    return session.query(AuditRuleModel).filter_by(id=rule_id).first() is not None
