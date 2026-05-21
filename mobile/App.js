import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import LeadsListScreen from './screens/LeadsListScreen';
import LeadDetailScreen from './screens/LeadDetailScreen';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen 
          name="Leads" 
          component={LeadsListScreen} 
          options={{ title: 'Well Beings — Leads' }} 
        />
        <Stack.Screen 
          name="LeadDetail" 
          component={LeadDetailScreen} 
          options={{ title: 'Lead Details' }} 
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}