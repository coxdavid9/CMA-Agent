import React from 'react';
import FlexibleBudgetWorkshop from './FlexibleBudgetWorkshop';
import ScenarioWorkshop from './ScenarioWorkshop';
import TransactionWorkshop from './TransactionWorkshop';
import {FINANCIAL} from './financialModels.mjs';
export default function LessonWorkshop(props){
 if(FINANCIAL[props.lesson.id])return <TransactionWorkshop {...props}/>;
 return props.lesson.id==='flexible-budget'?<FlexibleBudgetWorkshop {...props}/>:<ScenarioWorkshop {...props}/>;
}
