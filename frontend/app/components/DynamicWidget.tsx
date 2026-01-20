import React from 'react';
import { NewsWidget } from './widgets/NewsWidget';
import { VideoWidget } from './widgets/VideoWidget';
import { PlaceWidget } from './widgets/PlaceWidget';

interface DynamicWidgetProps {
    widget: {
        type: string;
        priority: number;
        data: any;
    };
}

export const DynamicWidget: React.FC<DynamicWidgetProps> = ({ widget }) => {
    switch (widget.type) {
        case 'news_card':
            return <NewsWidget data={widget.data} />;

        case 'video_widget':
            return <VideoWidget data={widget.data} />;

        case 'place_card':
            return <PlaceWidget data={widget.data} />;

        default:
            console.warn(`Unknown widget type: ${widget.type}`, widget);
            return null;
    }
};
