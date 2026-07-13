/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strrchr.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/24 14:04:51 by kyonaha           #+#    #+#             */
/*   Updated: 2026/04/28 16:28:37 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

char	*ft_strrchr(const char *str, int chr)
{
	int	idx;

	idx = ft_strlen(str);
	while (0 <= idx)
	{
		if (str[idx] == (unsigned char)chr)
			return ((char *)str + idx);
		idx--;
	}
	return (NULL);
}
