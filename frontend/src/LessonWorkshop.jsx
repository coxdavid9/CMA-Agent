import React from 'react';
import FlexibleBudgetWorkshop from './FlexibleBudgetWorkshop';
import ScenarioWorkshop from './ScenarioWorkshop';
export default function LessonWorkshop(props){
 return props.lesson.id==='flexible-budget'?<FlexibleBudgetWorkshop {...props}/>:<ScenarioWorkshop {...props}/>;
}
